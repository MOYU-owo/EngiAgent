from io import BytesIO

import json
import httpx
import pytest
from PIL import Image

from engi_agent.ui.ocr import recognize_image
from engi_agent.ui.service import WorkbenchSession, load_case
from engi_agent.engineering.roles import FixtureRoles


@pytest.fixture(autouse=True)
def credentials(monkeypatch):
    monkeypatch.setenv('DEEPSEEK_API_KEY','test-key')


def model_client(text='跨度 6m\n梁宽 300mm', status=200):
    def respond(request):
        body=json.loads(request.content)
        assert body['model']=='deepseek-flash'
        assert body['messages'][1]['content'][1]['image_url']['url'].startswith('data:image/png;base64,')
        return httpx.Response(status,json={'choices':[{'finish_reason':'stop','message':{'content':json.dumps({'text':text,'uncertainties':['核对单位']})}}]})
    return httpx.Client(transport=httpx.MockTransport(respond))


def picture():
    output=BytesIO()
    Image.new('RGB',(300,100),'white').save(output,format='PNG')
    return output.getvalue()


def test_image_text_then_dispatch_preserves_original_and_edited_query():
    result=recognize_image(picture(),client=model_client())
    assert result.text=='跨度 6m\n梁宽 300mm'
    assert result.width==300 and result.uncertainties==['核对单位']
    ctl=WorkbenchSession()
    ctl.parse(result.text+'\n请设计',roles=FixtureRoles(load_case('完整新方案设计')),
              image_evidence=result.evidence())
    assert ctl.case_name=='图片识别任务'
    assert [c.role for c in ctl.calls]==['VisionOCR','Dispatcher']
    assert ctl.calls[0].outputs['text']==result.text
    assert ctl.calls[1].inputs['query'].endswith('请设计')
    assert not ctl.draft.confirmed and ctl.result is None


@pytest.mark.parametrize('data',[b'', b'not an image', b'x'*(10*1024*1024+1)],ids=['empty','corrupt','over-limit'])
def test_invalid_images_never_invoke_engine(data):
    def forbidden(_):
        pytest.fail('Invalid input must not reach OCR')
    with pytest.raises(ValueError):recognize_image(data,client=forbidden)


def test_empty_recognition_is_actionable():
    with pytest.raises(ValueError,match='DeepSeek|识别'):
        recognize_image(picture(),client=model_client(text=''))


def test_oversize_pixels_rejected_before_inference():
    output=BytesIO()
    Image.new('1',(5000,4100)).save(output,format='PNG')
    with pytest.raises(ValueError,match='像素'):
        recognize_image(output.getvalue(),client=None)


@pytest.mark.parametrize('status',[400,401,402,429,500])
def test_cloud_error_is_safe_and_actionable(status):
    with pytest.raises(ValueError,match='DeepSeek'):
        recognize_image(picture(),client=model_client(status=status))
