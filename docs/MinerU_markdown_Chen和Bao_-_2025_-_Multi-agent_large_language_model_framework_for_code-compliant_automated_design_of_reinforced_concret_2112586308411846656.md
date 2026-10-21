# Multi-agent large language model framework for code-compliant automated design of reinforced concrete structures

![image](https://cdn-mineru.openxlab.org.cn/result/2026-10-21/373b0a38-2fcf-4fbd-8f5c-effe78e1d2e1/58867619398a7a3597f16500fae2f2790c18763807df0644c6f01f9ac1b3583c.jpg)


Jinxin Chen , Yi Bao 

Department of Civil, Environmental and Ocean Engineering, Stevens Institute of Technology, Hoboken, NJ 07030, USA 

## A R T I C L E I N F O

Keywords: Building code compliance Concrete structures Automated design Large language model Multi-agent framework Structural design 

## A B S T R A C T

The current manual approach for designing reinforced concrete, guided by structural design codes, is inefficient and susceptible to human error. This paper presents a Large Language Model (LLM) framework to automate codecompliant design and achieve interpretability and verifiability. The framework decomposes complex tasks into subtasks handled by coordinated LLM agents with specialized expertise, enabling automatic structural design and human-robot interaction for exploring alternative solutions and explanations. This framework was tested using case studies on the design and evaluation of 30 beams and compared against commercial engineering software SAP2000, demonstrating how the agents collaborate and cross-check results while maintaining high accuracy (97 %), high efficiency (90 % time-saving), and transparency in structural analysis and design. An intuitive Graphical User Interface (GUI) that supports natural language queries was developed to facilitate practical use. By bridging the gap between intuitive communication and rigorous structural analysis, this framework provides a paradigm shift for automatic structural design. 

## 1. Introduction

Structural design is a comprehensive task that transforms architectural concepts into safe, functional, and economically viable structures [1]. The task encompasses several interconnected phases: structural system configuration, load analysis, structural analysis, and member design, with code compliance checks throughout the process. Tradi tional design practices often rely on manual structural analysis and design according to codes. With advancements in computing techniques, modern structural design uses an ecosystem of software tools serving distinct yet complementary functions: Building Information Modeling (BIM) [2] enables sophisticated visualization and cross-discipline coor dination; structural analysis software, such as ETABS [3] and SAP2000 [4], handles complex load and structural analysis; and Computer-Aided Design (CAD) software [5] facilitate drafting. The synergy between structural knowledge and computational tools has proven effective in providing reliable and verified design solutions through decades of practical applications. 

The above structural design approach is challenged by the increasing complexity of modern structures, compressed project timelines, and demands for more sustainable solutions. Engineers face mounting pressure to explore alternative design, optimize material usage, and achieve design solutions faster while retaining unwavering safety and code compliance. The evolving challenges have sparked interest in Artificial Intelligence (AI) applications for structural design tasks. 

Machine Learning (ML) approaches have been applied across multiple aspects of structural design: generating and optimizing structural system configurations [6,7], predicting structural responses [8,9], and optimizing structural sizing [10,11]. Furthermore, sophisticated ML techniques have shown significant promise in the complex assessment and prediction of seismic performance and risk for Reinforced Concrete (RC) structures. For instance, recent research has explored optimizationbased stacked ML methods and various ML algorithms with advanced hyperparameter optimization for seismic probability, risk, fragility, and vulnerability assessment of RC shear walls and frames. These studies have achieved high accuracy in predicting relevant metrics from extensive datasets generated via incremental dynamic analysis, exemplifying how ML can be applied to evaluate RC structures and their vulnerability to seismic events based on simulation data [12,13]. The effectiveness of these applications has demonstrated potential to transform traditional structural design workflows while enhancing efficiency in time, labor, and cost [14,15]. However, fundamental limitations persist in structural design using black-box ML models with low interpretability and verifiability [16,17]. 

These limitations become particularly critical in structural analysis and design. Paradoxically, while ML models may achieve high accuracy [18,19], this seemingly favorable outcome raises concerns for engineers because ML results may violate code provisions. Furthermore, the accuracy of ML models is dependent on the quality of the training dataset, which can be reduced by data bias [20]. Although various strategies have been developed to train ML models on limited data [21], the verification challenges raise safety concerns that confine applications to research contexts or preliminary design phases. Unlike system configurations that engineers can verify through independent analysis, models predicting structural responses or suggesting member sizes produce results that cannot be easily validated without recreating the entire design process. These verification challenges raise safety concerns that confine AI applications to research contexts or preliminary design phases. 

The emergence of Large Language Models (LLMs) [22] offers new opportunities of structural design. Unlike traditional black-box ML models that produce outputs without explanation, LLMs possess remarkable abilities to understand and generate natural language, reason through complex requirements, and explain their analysis processes step-by-step, enabling engineers to interact with LLMs through asking questions, specifying requirements, and receiving detailed ex planations that mirror how engineers naturally communicate and solve problems [23]. LLMs have demonstrated promising abilities to under stand building codes through fine-tuned transformer models [24], automate construction reporting via multimodal frameworks [25], and predict seismic responses using physics-informed approaches [26]. 

However, LLMs face a critical reliability limitation that prevents their direct application to structural design due to a fundamental precision problem in two aspects: factual hallucinations when addressing engineering knowledge and computational errors when executing calculations [27–30]. This dual reliability issue means LLMs may generate plausible-sounding but incorrect solutions violating code provisions or design principles or making errors in calculations despite following conceptually sound procedures. Given that structural design fundamentally relies on both accurate engineering knowledge and precise calculations to ensure safety, this reliability limitation creates a signif icant barrier to applying LLMs to safety-critical tasks. 

To address these challenges, this paper presents a collaborative multi-agent LLM approach based on a framework that breaks down complex structural design tasks into subtasks handled by dedicated LLM agents with specific expertise in areas like load and structural analysis, member sizing, or reinforcement design. An LLM agent is a specialized instance of an LLM assigned with a specific role, expertise, and abilities [31]. Rather than modifying the intrinsic architecture of the models, the approach acknowledges these reliability limitations and mitigates them through: (1) integration with external deterministic tools that perform accurate calculations, and (2) generating transparent, step-by-step explanations that make the outputs verifiable by human engineers against code compliance and design standards. This human verification is a critical component of the proposed framework, ensuring that safety critical decisions are subject to professional oversight. The agents are coordinated for information sharing and cross-checking results while maintaining a transparent record of subtasks. This agent-based approach has been inspired by recent research on trip planning [32] and resume screening [33]. The applications of LLM agents remain under-explored in the context of structural design. 

To develop the multi-agent LLM approach, key research questions must be answered: How can LLM agents be coordinated to perform codecompliant structural design and evaluation? How does the proposed design approach perform? How can the approach be used by practitioners? Guided by these questions, the objectives of this research are to (1) develop a framework that integrate and coordinate LLM agents to collaboratively execute complex design tasks while maintaining transparency and verifiability; (2) evaluate the performance of the approach via case studies on structural design and evaluation; and (3) develop an accessible Graphical User Interface (GUI), facilitating practitioners to 

implement the approach. 

This research has three main contributions: (1) A new approach is developed to enable code-compliant structural design with automation and minimal hallucination. (2) The concept of multi-agent LLM systems is used to develop an AI-powered design framework with high inter pretability and verifiability. (3) Human-robot interactions for reasoning and improving structural design solutions are integrated into the auto matic design framework, along with an accessible GUI. 

The remainder of the paper is organized as follows: Section 2 presents the proposed approach. Section 3 presents a case study of structural design. Section 4 presents a case study of structural evaluation. Section 5 introduces the GUI. Section 6 discusses the validation framework, strengths, and weaknesses of the approach. Section 7 summarizes the conclusions. 

## 2. Proposed approach

This section presents the multi-agent framework and elaborates the primary components. First, an overview of the framework is presented (Section 2.1), followed by elaboration of the agents, including Task Dispatcher (Section 2.2), design and evaluation agents (Section 2.3), and Expert Consultation (Section 2.4). Finally, the criteria for the selection of case studies used to evaluate the proposed approach are elaborated (Section 2.5). 

## 2.1. Overview of the multi-agent framework

The proposed multi-agent framework orchestrates structural design and evaluation workflows via a collaborative architecture that ensures precision, reliability, and transparency. As shown in Fig. 1, the framework creates a seamless progression from initial user query to final solution, with verification mechanisms at each stage to ensure the technical validity of outputs. 

The core of this framework is a distributed intelligence approach where specialized agents handle distinct aspects of the structural design process, coordinated through a central query routing system. The modular architecture addresses the fundamental limitations of using LLMs to design structures, namely their tendency toward factual hallucinations when addressing domain-specific knowledge and computational errors when executing calculations. The framework consists of the following key agents, each with specific responsibilities: 

• Task Dispatcher Agent: Serves as the initial interface with users and functions as an Optical Character Recognition (OCR)-enhanced agent capable of processing both textual and image-based inputs. This agent analyzes queries, classifies them into design or evaluation tasks, extracts relevant parameters, and routes them to the appropriate specialized agent. 

• Structure Design Agent: Focuses on generating new structural designs based on user requirements. This agent accepts relevant parameters from queries, coordinates appropriate tool sequences, and leverages specialized engineering tools to provide code-verified design solutions that adhere to regulatory standards. 

• Design Evaluation Agent: Specializes in assessing existing structural designs against code requirements. When provided with specifications of an existing structure, this agent processes the information to conduct code-compliant evaluations, interfacing with specialized tools to verify compliance with both strength and serviceability criteria. 

• Code-based Knowledge Component: Serves as a central repository integrating two critical elements: (1) specialized calculation tools programmed to implement specific design code requirements, and (2) actual code provisions. This dual-nature repository ensures that all solutions strictly comply with design codes through reliable computation while providing reference to the original regulatory language. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-10-21/373b0a38-2fcf-4fbd-8f5c-effe78e1d2e1/cbd2a583374ddcc023758f426454236cda3be21722d213b9f5a62c7bf0be5d94.jpg)



Fig. 1. Multi-agent framework.


• Expert Consultation Agent: Facilitates follow-up interactions by accessing stored design or evaluation results alongside relevant codes. This agent maintains context throughout user interactions while ensuring code compliance, providing additional insights or modifications based on previous results when users present querie about design or evaluation outcomes. 

The workflow begins when a user submits a design or evaluation query. The Task Dispatcher analyzes and classifies the task, directing it to either the design or evaluation pathway while extracting relevant parameters. In the design path, the Structure Design agent coordinates tool sequences to provide code-compliant solutions. Similarly, in the evaluation path, the Design Evaluation agent conducts code-compliant assessments of existing designs. 

Both pathways interface with the Code-based Knowledge component, which integrates specialized calculation tools programmed to implement specific code requirements alongside the code provisions in text form. This dual-nature knowledge repository is crucial to the framework’s reliability. The structured tools handle precise calculations according to code formulas, while the textual provisions support veri fication, explanation, and contextual understanding of designs. 

By separating code-compliant calculations from the LLM’s reasoning process, this approach effectively prevents hallucination in structural design and evaluation tasks while maintaining calculation accuracy. The culmination of either path leads to solutions that are both technically precise and understandable, representing an approach that integrates regulatory requirements with AI capabilities to achieve both code compliance and intuitive user interaction. 

## 2.2. Task dispatcher

The Task Dispatcher functions as the initial interface and query routing mechanism, serving as the entry point of the approach. This component is responsible for processing natural language queries and determining the appropriate workflow path for each request as shown in Fig. 2. 

When a user submits a preliminary design or evaluation query, the Task Dispatcher employs a multi-step processing approach: First, the Task Dispatcher performs task classification to class the query into one of three categories, which are design-related, evaluation-related, or unrelated. This classification leverages natural language processing techniques to identify key intent markers and domain-specific terminology within the user’s query. For queries classified as either design or evaluation tasks, the Task Dispatcher proceeds to parameter extraction. This process involves identifying and isolating critical engineering parameters embedded within the natural language input, such as dimensional specifications, material properties, loading conditions, or applicable code requirements. The extraction process transforms unstructured natural language into structured parameter sets that can be processed by downstream specialized agents. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-10-21/373b0a38-2fcf-4fbd-8f5c-effe78e1d2e1/bcfd44efbc3fe75a49f46819e5cdb14e4ba182557e8ff612ac16636292f7831a.jpg)



Fig. 2. Flowchart of task dispatcher.


Based on the classification results, the Task Dispatcher then routes the query and its extracted parameters to the appropriate path: 

• Design-related queries are directed to the Structure Design agent along with relevant extracted parameters. 

• Evaluation-related queries are channeled to the Design Evaluation agent with their corresponding parameters. 

• Queries classified as unrelated trigger a response requesting clarifi cation or indicating the system s limitations. 

By serving as an intelligent routing mechanism, the Task Dispatcher ensures that each query reaches the most appropriate specialized com ponents within the system, optimizing the response quality while maintaining the technical precision required for engineering applications. 

## 2.3. Automation agents for design and evaluation

The design and evaluation automation agents are parallel components that share the technical infrastructure. The specialized agent enable structural design and evaluation through an integrated system of deterministic calculation tools, ensuring accuracy while maintaining a conversational interface for users. The automation agents coordinate comprehensive design and evaluation tasks. The core engineering tools are rule-based deterministic programs implemented by the authors according to code provisions. These tools include: 

• Cross-section determination tool: Implements minimum dimensional requirements from building codes for reinforced concrete elements, following appropriate provisions for preliminary sizing based on structural type, span length, and support conditions. 

• Load analysis tool: Calculates load combinations according to code provisions, determining design loads for both strength and serviceability requirements with appropriate safety factors applied to dead and live loads. 

• Structural analysis tool: Performs element analysis using standard mechanics principles to determine maximum moment and shear demands based on the load combination. 

• Flexural design tool: Calculates the cross-sectional area of steel reinforcement required to resist the design moment while ensuring code compliance regarding minimum and maximum reinforcement ratios and proper spacing as specified in relevant code sections. 

• Shear design tool: Utilizes structural analysis results and flexural design outcomes to determine appropriate stirrup spacing, with particular attention to requirements specified in code provisions for shear reinforcement. 

• Evaluation check tools: Function as counterparts to each design tool, taking existing design parameters as inputs to verify compliance with code requirements. These tools include cross-section checks, flexural and shear design checks, and serviceability assessment tools that verify deflection requirements according to code provisions. 

Given the parameters extracted from the Task Dispatcher, each LLM agent first determines the appropriate tool sequence for completing the task. This sequence determination is performed by a specialized workflow planning module that analyzes available parameters, identifies missing information, and constructs the most complete execution path possible with given inputs. Unlike traditional software requiring complete input, this approach offers flexibility as the system can proceed with partial information, completing as many steps as possible rather than failing due to incomplete input. 

After establishing the implementation sequence, the agent executes each step by calling the corresponding deterministic calculation modules. Each calculation module is coded to precisely implement specific code provisions and engineering formulas, performing calculations ac cording to code requirements with mathematical exactitude. The LLM then receives standardized results from these tools and generates human-readable responses that include calculation steps and references to specific code provisions. This architecture is critical for preventing the hallucination of LLM, as the LLM does perform calculations but instead relies on verified deterministic modules. 

The outcomes of these tools are stored in a structured format, with intermediate and final results for traceability. Fig. 3 shows the parallel workflows of design and evaluation tasks, highlighting shared calculation components and domain-specific differences in their distinct ob jectives and tool requirements. This unified approach to automation ensures consistency across the system while allowing each agent to address specific requirements. By maintaining a common architectural framework, the system facilitates knowledge sharing between components while preserving the specialized abilities required for each task. 

## 2.4. Expert consultation

The Expert Consultation agent facilitates follow-up interactions by accessing stored design or evaluation results and relevant codes. This component serves as the system’s conversational memory, enabling users to engage in multi-turn discussions about design solutions or evaluation outcomes while maintaining technical accuracy and code 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-10-21/373b0a38-2fcf-4fbd-8f5c-effe78e1d2e1/66fef5270b1bf7da7ebc177c342d686597099f8507d134a55a1ada0df3b4dd38.jpg)



Fig. 3. Automation workflow for design and evaluation agents.


compliance. 

The agent uses LLM architecture designed to balance natural language understanding with rigorous engineering precision. This archi tecture was developed to overcome a challenge: User queries are unpredictable, making it impossible to standardize the interaction pro cess. Unlike the design and evaluation paths, which follow well-defined procedures, follow-up queries may explore diverse aspects of a design, request clarification on specific calculations, or investigate alternative scenarios that weren’t initially considered. 

This unpredictability requires that the system should provide conversational freedom while addressing a critical concern in structural engineering applications. When embedded with relevant code compli ance documentation and stored design or evaluation results, LLMs have the ability to adhere to given text and provide responses that reference specific codes and previously calculated values. However, the key challenge remains that LLMs alone cannot reliably perform complex calculations, which are virtually inevitable in structural engineering applications. To resolve this tension between conversational flexibility and calculation precision, the paper proposes a three-component LLM architecture as shown in Fig. 4. 

The primary LLM receives user queries along with relevant context from prior interactions and stored results. It generates a complete response directly, interpreting the query and formulating an answer that may include calculations. This response prioritizes natural language understanding and conversational fluidity, but the calculations may have errors. The system accepts this limitation at this stage, allowing the primary LLM to focus on comprehensive response generation. 

The verification LLM then examines the primary LLM’s response, specifically focusing on identifying and validating any calculations. This component, integrated with specialized calculator tools, recalculates all numerical values, checking them against established engineering formulas and code requirements. When discrepancies are found, the verification LLM will correct the errors of calculations while maintaining the original context and explanation structure. 

Finally, the integrator LLM combines the original response from the primary LLM with the corrected calculations from the verification LLM. This final component creates a coherent, unified response that preserves the conversational quality and contextual understanding of the primary LLM while achieving high precision ensured by the verification LLM. The result is a response that appears seamless to the user while guaranteeing calculation accuracy. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-10-21/373b0a38-2fcf-4fbd-8f5c-effe78e1d2e1/5d8176dc21e594f5e6ba7398b20acce07b422f51bc69161a02918c6ecc43f585.jpg)



Fig. 4. Flowchart of expert consultation.


This sequential processing approach enables the system to leverage the strengths of each component: the primary LLM’s conversational ability, the verification LLM’s calculation precision, and the integrator LLM’s synthesis ability. The architecture maintains access to both design and evaluation databases. This unified access ensures consistent handling of follow-up inquiries while maintaining domain-specific compliance considerations. 

However, the three-LLM architecture introduces additional latency due to its sequential processing nature. The system implements a userchoice setting that allows users to select between using just the primary LLM alone for straightforward queries or the full three-LLM architecture for calculation-intensive tasks. This option provides a balance between efficiency and accuracy based on the specific requirements of each query. For routine questions that do not involve complex calculations, users can leverage the faster response time of the single-LLM approach. When accurate numerical validation becomes critical, the comprehen sive three-LLM pipeline can be utilized to achieve high accuracy. 

The Expert Consultation agent ultimately transforms the system from a one-time query processor into a collaborative engineering assistant capable of technically precise interaction. By maintaining both conversational context and calculation accuracy, it has the potential to enable users to query complex questions through natural dialogue while benefiting from the system’s computational rigor and code compliance expertise. 

## 2.5. Criteria for study selection

The framework has been evaluated through case studies, which were selected based on three primary criteria: 

• First, reinforced concrete beams were selected as the structural element for evaluating the proposed framework because they represents a type of basic structural elements. These beams incorporate essential structural design principles including flexural analysis, shear design, and serviceability evaluation, making them ideal can didates for evaluating the performance of the framework without having to handle unnecessary complex geometry. This selection provides a manageable task while requiring comprehensive engineering knowledge and multiple code-compliant analysis. 

• Second, ACI 318 was selected as the governing code standard due to its wide adoption in North American and explicit computational procedures. This selection provides a rigorous regulatory standard for verifying strength and serviceability requirements. The code’s comprehensive provisions for reinforced concrete design spanning material properties, load factors, analysis procedures, and detailing requirements offer sufficient complexity to test the proposed system’s ability to interpret and implement regulatory language while performing precise calculations according to standardized procedures. 

• Third, design cases with reference solutions documented in pub lished literature were prioritized to ensure verifiability. This criterion was crucial for validating the accuracy of the framework’s outputs against independent results, establishing a clear benchmark for assessing the framework’s performance. 

A design example of reinforced concrete beams was selected from StructurePoint [34] as the primary test case as it satisfies all required criteria and involves straightforward loading conditions. The example follows ACI 318 provisions with step-by-step calculations, offering a comprehensive reference solution that includes member dimensions, reinforcement areas, load capacities, and deflections. This example serves as an ideal benchmark for evaluating the framework’s ability to generate designs that are structurally sound and code-compliant while allowing direct comparison against a verified industry solution. 

## 3. Case study 1: design of a reinforced concrete beam

For this case study, DeepSeek-V3 [35] was used as the foundation model via its Application Programming Interface (API) due to its balance of performance, computational efficiency, and cost-effectiveness [36]. The considered regulatory code is ACI 318–19 [37], and imperial units have been adopted in this case study for consistency with ACI 318–19. 

## 3.1. Preliminary query classification and processing

As the first step in the design process, the Task Dispatcher agent receives and analyzes the user query (Fig. 5). The Task Dispatcher interface receives a complete set of design parameters, including concrete strength 4.35 ksi (30 MPa), concrete weight 150 lb/ft<sup>3</sup> (2400 kg/ $\mathbf { m } ^ { 3 } ) ,$ , steel yield strength 60 ksi (413.7 MPa), dead load of 0.82 kip/ft. (12.0 kN/m), live load of 1.00 kip/ft. (14.6 kN/m), span length 25 ft. (7.6 m), and reinforcement detail (#9 longitudinal bars and #3 stirrups). Inputting design specifications in an image format rather than texts demonstrates the framework’s OCR-enhanced text capabilities. A typical query that a structural engineer submits when seeking assistance with beam design is presented. 

The Task Dispatcher processes this query to determine the appropriate workflow path and extract relevant design parameters. Table 1 presents the output of the classification and parameter extraction process. 

## 3.2. Design process and results

After the Task Dispatcher classifies the query and extracts relevant parameters, the system routes the request to the Structure Design agent. Given these extracted parameters, the workflow planning tool within the agent identifies the specific sequence of steps that can be implemented with the available information. Based on this analysis, the LLM agent logically calls specialized tools in sequence according to the workflow planning results: 

• Preliminary Sizing: Determination of initial beam dimensions. 

• Load Analysis: Determination of factored load combinations and maximum factored loads. 

• Structural Analysis: Calculation of maximum moment and shear demand. 

• Flexural Design: Determination of longitudinal bar area and rein forcement configuration. 

• Shear Design: Calculation of required stirrup spacing and stirrup configuration. 

This sequence follows established structural engineering workflows while maintaining full transparency and code compliance at each step. Importantly, the system maintains parameter continuity between steps, where outputs from earlier tools serve as inputs to subsequent tools in the chain. For example, beam dimensions from the preliminary sizing step are used in subsequent calculations. Structural analysis results provide the maximum moment and shear values needed for 

I need help designing a simply-supported reinforced concrete beam with the following specifications: 

· Concrete strength: 4.35 ksi 

· Concrete weight: 150 Ib/ft³ 

· Steel yield strength: 60 ksi 

· Dead load: 0.82 kip/ft (excluding self-weight) 

· Live load: 1.00 kip/ft 

· Span length: 25 ft 

· Reinforcement: #9 bars (longitudinal) 

• Stirrups: #3 bars 

• Clear cover: 1.5 inches 

· Maximum aggregate size: 0.75 inches 

Fig. 5. Design specifications for a simply-supported reinforced concrete beam. 


Table 1



Query classification and parameter extraction results.


<table><tr><td>Component</td><td colspan="4">Result</td></tr><tr><td>Task classification</td><td colspan="4">DesignThe query requests assistance in designing a new reinforced concrete beam, including specifications for materials, loads, and reinforcement, which indicates a need for creating new beam designs.</td></tr><tr><td rowspan="6">Reasoning</td><td rowspan="2">Parameter category</td><td>Parameter</td><td>Value</td><td>Unit</td></tr><tr><td>Span length</td><td>25</td><td>ft</td></tr><tr><td rowspan="3">Geometry</td><td>Beam depth</td><td>-</td><td>in</td></tr><tr><td>Beam width</td><td>-</td><td>in</td></tr><tr><td>Dead load</td><td>0.82</td><td>kip/ft</td></tr><tr><td>Loads</td><td>Live load</td><td>1.00</td><td>kip/ft</td></tr><tr><td rowspan="7">Extracted parameters</td><td></td><td>Concrete strength</td><td>4.35</td><td>ksi</td></tr><tr><td rowspan="3">Concrete</td><td>Unit weight</td><td>150</td><td>lb/ft<eq>^{3}</eq></td></tr><tr><td>Maximum aggregate size</td><td>0.75</td><td>in</td></tr><tr><td>Longitudinal diameter</td><td>1.128</td><td>in</td></tr><tr><td rowspan="3">Reinforcement</td><td>Stirrup diameter</td><td>0.375</td><td>in</td></tr><tr><td>Longitudinal yield strength</td><td>60</td><td>ksi</td></tr><tr><td>Stirrup yield strength</td><td>60</td><td>ksi</td></tr></table>

reinforcement design. 

The process begins with preliminary member sizing. Requirements of the minimum depth are specified in ACI 318–19. This critical step establishes the foundational beam dimensions that affect subsequent subtasks. The system identifies relevant requirements from Table 9.3.1.1 of ACI 318–19 and determines the minimum beam depth based on span length and support conditions. 

Following preliminary sizing, the load analysis tool calculates load combinations according to Table 5.3.1 of ACI 318–19, determining the design loads strength requirements, accounting for the different safety factors applied to dead and live loads as mandated by ACI 318–19. The structural analysis tool then processes these loads to determine the maximum moment and shear demands based on the load combination results from the previous step. 

With these preliminary results of member size and structural analysis, the flexural design tool determines the required steel bar area and arrangement of #9 bars. This step involves calculating the crosssectional area of steel bars required to resist moment while ensuring code compliance regarding the minimum and maximum reinforcement ratios and proper spacing as per clause 9.6.1.2, Table 20.6.1.3.1, Table 22.2.2.4.3, and Table 24.3.2 of ACI 318–19. 

Subsequently, the shear design tool utilizes both the structural analysis results and flexural design outcomes to determine appropriate stirrup spacing using #3 bars. This calculation is critical as it ensure that the beam can resist diagonal tension forces, with particular atten tion to spacing requirements according to clauses 9.7.6.2.2, 10.6.2.2, 22.5.1.1, 22.5.1.2, and Table 22.5.1. 

This sequential process demonstrates how the LLM framework orchestrates multiple design tools while maintaining calculation accuracy and code compliance. Each specialized tool performs its calculations with mathematical precision according to relevant code provisions, while the Structure Design agent coordinates the overall process and ensures proper data flow between tools. 

The design results from the proposed approach are compared with the design results from reference [34], as shown in Table 2, showing good agreement and verifying the accuracy of the proposed approach. The responses of LLM agents are presented in Supplementary Materials, providing the complete reasoning process, calculation steps, and code checks. This transparency allows engineers to verify the design process, with traceable calculations, explicit references to relevant codes, and explicit explanations of design decisions using relevant terminology. 


Table 2



Design results from sequential tool processing.


<table><tr><td>Design step</td><td>Parameter</td><td>LLM result</td><td>Reference result</td><td>Reference to ACI 318-19</td></tr><tr><td rowspan="3">Preliminary sizing</td><td>Beam width</td><td>12 in (305 mm)</td><td>12 in (305 mm)</td><td rowspan="3">Table 9.3.1.1</td></tr><tr><td>Beam depth</td><td>20 in (508 mm)</td><td>20 in (508 mm)</td></tr><tr><td>Factored dead load</td><td>0.98 kip/ft (14.3 kN/m)</td><td>0.98 kip/ft (14.3 kN/m)</td></tr><tr><td rowspan="3">Load analysis</td><td>Factored live load</td><td>1.60 kip/ft (23.4 kN/m)</td><td>1.60 kip/ft (23.4 kN/m)</td><td rowspan="3">Table 5.3.1</td></tr><tr><td rowspan="2">Total factored load</td><td>2.58 kip/ft (37.7 kN/m)</td><td>2.58 kip/ft (37.7 kN/m)</td></tr><tr><td>201.88 kip-ft (273.7 kN·m)</td><td>201.88 kip-ft (273.7 kN·m)</td></tr><tr><td rowspan="3">Structural analysis</td><td>Maximum moment</td><td>32.3 kip (143.7 kN)</td><td>32.3 kip (143.7 kN)</td><td rowspan="5">Clause 9.6.1.2, Table 20.6.1.3.1, Table 22.2.2.4.3</td></tr><tr><td>Maximum shear force</td><td>2.869 in<eq>^{2}</eq> (1850 mm<eq>^{2}</eq>)</td><td>2.872 in<eq>^{2}</eq> (1853 mm<eq>^{2}</eq>)</td></tr><tr><td>Required longitudinal reinforcement area</td><td></td><td></td></tr><tr><td rowspan="5">Flexural design</td><td>Provided longitudinal reinforcement area</td><td>3.00 in<eq>^{2}</eq> (1935 mm<eq>^{2}</eq>)</td><td>3.00 in<eq>^{2}</eq> (1935 mm<eq>^{2}</eq>)</td></tr><tr><td>Bar arrangement</td><td>3#9</td><td>3#9</td></tr><tr><td>Spacing of longitudinal reinforcement</td><td>3.56 in (90.4 mm)</td><td>3.38 in (85.9 mm)</td><td rowspan="3">Clause 24.3.2.1 Table 24.3.2</td></tr><tr><td>Concrete capacity</td><td>20.85 kips (92.8 kN)</td><td>20.85 kips (92.8 kN)</td></tr><tr><td>Required shear reinforcement strength</td><td>10.23 kips (45.5 kN)</td><td>10.23 kips (45.5 kN)</td></tr><tr><td rowspan="3">Shear design</td><td>Stirrup configuration</td><td>14- #3@8.5 in (14- #3@216 mm)</td><td>16-#3@8.3 in (16- #3@211 mm)</td><td rowspan="3">Table 9.7.6.2.2, clauses 10.6.2.2 22.5.1.1, 22.5.1.2, Table 22.5.5.1</td></tr><tr><td>Final capacity</td><td>41.30 kips (183.7 kN)</td><td>41.79 kips (185.9 kN)</td></tr><tr><td>Cutoff points</td><td>101.44 in (2577 mm) from support</td><td>101.59 in (2580 mm) from support</td></tr></table>

The agreement with the reference solution not only validates the accuracy of the deterministic tools integrated within the framework but also demonstrates advantages over earlier AI approaches. While prior ML models were able to predict structural parameters [38], they lacked the verifiable, step-by-step, code-compliant reasoning abilities. Furthermore, by coordinating specialized agents to achieve a code compliant design through natural language interaction, this result addresses the reliability and precision challenges identified with LLM applications in engineering calculations. 

## 3.3. Design enhancement through expert consultation

After generating the initial design, the system allows for iterative refinement through multi-round interaction with the user. This capability leverages the Expert Consultation agent, which provides techni cally accurate responses to follow-up queries while maintaining code compliance throughout the design evolution process. The results from the interaction sequence are listed in Table A1 (Appendix). The process 

unfolds as follows: 

Inquiry 1: In which way can we reduce cost while maintaining required capacities? 

The LLM agent responds with a comprehensive cost optimization strategy that addresses holistic aspects of cost-saving strategies across materials, labor, and construction methods. For material use, the agent suggests refining the cross-section to reduce concrete volume while meeting code requirements, and recommends using standard dimensions to minimize formwork costs. For reinforcement, the agent proposes using fewer bars and potentially employing higher-strength steel (e.g., ASTM Grade 75) to reduce steel mass. The response includes innovative approaches such as exploring fiber-reinforced concrete to reduce steel bars and considering precast options to save labor and formwork costs. Throughout these recommendations, the agent demonstrates awareness of practical construction considerations by suggesting reusable formwork and recommending value engineering reviews with contractors to identify further cost-saving opportunities. This comprehensive response demonstrates the system’s ability to generate practical design alternatives that consider both technical per formance and economic factors. 

Inquiry 2: Please give a specific plan about using large-diameter bars. 

The LLM agent provides a detailed redesign plan focused on opti mizing steel reinforcement. The plan centers on replacing the original three #9 bars with two #11 bars at the bottom of the beam while maintaining #3 stirrups at 8.5-in. spacing for shear reinforcement. The agent offers precise calculations to ensure proper edge distance and spacing for the larger bars, confirming that the revised arrangement satisfies all code requirements. Beyond the technical specifications, the agent offers a thorough cost-benefit analysis comparing the original and revised designs. From a labor perspective, the agent explains that fewer bars significantly reduce placement and tying time, while the simplified layout minimizes the risk of construction errors. For material considerations, the analysis shows that while two #11 bars (3.12 in<sup>2</sup> (2013 mm<sup>2</sup>)) provide slightly more steel area than three #9 bars (3.00 in<sup>2</sup> (1935 mm<sup>2</sup>)), the minor increase in material cost is more than offset by substantial labor savings. The calculations demonstrate that the revised design with fewer, thicker bars maintains adequate moment capacity while satisfying relevant code requirements, including minimum and maximum reinforcement ratios, development length requirements, and spacing considerations. 

Inquiry 3: If we use two #11 bars, how do we ensure the beam is tension-controlled? 

To address the critical question of ductile behavior in the revised design, the user queries the tension-controlled status of the beam with two #11 bars. The LLM agent responds with a rigorous analysis that examines the parameters governing ductile failure mechanisms. The analysis begins with calculating the neutral axis depth, which the agent determines to be 5.07 in. (129 mm) from the bottom of the beam. Based on this position, the agent then calculates the net tensile strain in the extreme tension reinforcement as 0.0074, which exceeds the minimum threshold of 0.005 required by ACI 318–19 for a section to be classified as fully tension-controlled. The agent explains that although the neutral axis position shifts with the new reinforcement configuration (using fewer but larger bars), it remains well within acceptable limits to ensure ductile failure behavior. This analysis demonstrates the ability to perform nuanced structural calculations that address safety-critical aspects of the design while offering justifications for design decisions. 

Inquiry 4: In a corrosive environment, does the current spacing between two #11 bars still satisfy code requirements? 

In the final query, the user challenges the agent’s adaptability by introducing environmental constraints that would alter code requirements. The LLM agent recognizes the implications of a corrosive environment on reinforced concrete design and provides a comprehensive durability analysis. The agent first identifies that corrosive condi tions necessitate an increased clear cover from the standard 1.5 in. (38 mm) to 2 in. (51 mm) to comply with ACI 318–19 durability provisions. With the modified constraint, the agent recalculates the spacing between the two #11 bars as 5.84 in. (148 mm), and verifies that this spacing satisfies both the minimum requirements for concrete placement and the maximum limits for crack control. 

The agent extends its analysis beyond the spacing question and provides practical engineering recommendations for the corrosive environment scenario, including the formal implementation of the increased clear cover, confirmation that the current bar arrangement remains viable with the adjusted spacing, and consideration of enhanced protection measures such as epoxy-coated or stainless steel reinforcement for severely corrosive conditions. This response demonstrates the system’s ability to adapt design parameters to special environmental conditions while maintaining code compliance, showing how the framework can handle real-world design modifications that require both technical knowledge and practical engineering judgment. 

The LLM agent exhibits robust performance throughout the interactive design refinement process, delivering solutions that adhere to ACI 318–19 while maintaining calculation accuracy. Its effectiveness stems from seamless integration with two critical components: 

• Design results: The agent leverages outputs from prior design agent (e.g., initial moment/shear calculations, reinforcement layout parameters) to dynamically adjust recommendations while preserving structural integrity. This allows it to propose meaningful alternatives without compromising safety or performance requirements. 

• Integrated code compliance: The system performs real-time checks against relevant design standards to ensure continuous code compliance through all design iterations. For instance, when addressing the corrosion environment scenario, the agent automat ically applies the appropriate clear cover requirements and recal culates spacing limitations according to the specific provisions in ACI 318–19. 

This multi-round interaction demonstrates how the system supports an iterative design process that mirrors real-world engineering practice, where designs evolve through collaborative refinement. The ability of the Expert Consultation agent to explore design alternatives interactively, providing both technical validation and practical cost-benefit analysis, signifies a significant advancement beyond traditional and AI-based design methods. While recent work [39] developed ML models for flexural design optimization, the approach was limited without the capacity of interactive refinement. Conventional structural analysis software like SAP2000 [4] offers powerful tools for structural analysis and design, but it lacks the natural language interface for design exploration through conversation. The framework showcases the potential for AI agents to act as collaborative partners in the optimization process, offering interactive refinement abilities that are unavailable in traditional structural analysis software or previous automated design methods. 

## 4. Case study 2: evaluation of a reinforced concrete beam

This case study demonstrates the framework’s serviceability evalu ation capability through deflection analysis, representing a fundamentally different application scenario from Case Study 1. While the same beam parameters are used, this intentionally illustrates two distinct use cases: automated code-compliant design generation and existing design evaluation. The design from Case Study 1 serves as the evaluation sub ject solely for page simplicity since its code compliance has been demonstrated. This allows focused examination of deflection behavior without repeating the verification of other limit states. Deflection evaluation is a necessary complement to the design based on strength criteria, ensuring that the beam has adequate load capacity and serviceability. 

Table 5 

## 4.1. Preliminary query classification and processing

For this second case study, the user submits a query requesting an evaluation of the previously designed beam as shown in Fig. 6. The query is a structured input with complete specifications of the reinforced concrete beam. It shows key parameters: a 25-ft (7.6 m) span with crosssectional dimensions of 20 in. (508 mm) deep and 12 in. (305 mm) wide, subject to a dead load of 0.82 kip/ft. (12.0 kN/m) and live load of 1.00 kip/ft. (14.6 kN/m). The material properties include the 28-day compressive strength of concrete 4.35 ksi (30 MPa), a unit weight of 150 lb. $/ \mathrm { { f t } } ^ { 3 } ( 2 4 0 0 \mathrm { { k g } } / \mathrm { { m } } ^ { 3 } )$ , and steel yield strength of 60 ksi (413.7 MPa). For reinforcement, three #9 longitudinal bars are used for flexural resistance, and 14 #3 stirrups spaced at 8.5 in. (216 mm) for shear resistance. This comprehensive input is the design output from Case Study 1 and submitted for structural performance evaluation and code compliance verification. 

The Task Dispatcher processes this query to determine the appropriate workflow path and extract relevant parameters. Table 4 shows the classification result and parameters extracted. 

## 4.2. Deflection analysis

Upon receiving the evaluation query, the workflow planning tool of the Design Evaluation agent identifies multiple assessment steps, which are cross-section check, capacity verification, reinforcement check, and serviceability assessment. Since the beam was designed in Section 3, this section focuses on the serviceability assessment tool for critical deflection analysis. 

The serviceability assessment tool implements the deflection calculation method prescribed in Section 24.2 of ACI 318–19, considering both immediate and long-term deflections. The process follows the standard engineering approach, beginning with the determination of the modulus of rupture and cracking moment, followed by calculation of gross and cracked section properties. The tool then analyzes the effective moment of inertia using the equations in ACI 318–19, accounting for the partially cracked state under service loads. Throughout this process, the tool performs automatic code compliance checks, considering relevant provisions including clauses 19.2.2.1 and 19.2.3.1, as well as Tables 24.2.2 and 24.2.3.5. 

The deflection analysis results are shown in Table 5, which demon strates agreement between the agent’s calculations and reference results, validating the accuracy of the proposed approach for serviceability evaluation. The deflection analysis reveals that while the beam satisfies all strength requirements (Section 3), it exceeds the allowable long-term deflection limit 1.25 in (31.75 mm). This finding demonstrates how the evaluation path complements the design path by identifying serviceability issues that would not be captured by strength criteria. The detailed calculations supporting these results are presented in the 

I need help with an evaluation for the simply supported beam we just designed. The beam has the following specifications: 

• Span: 25 feet 

• Dimensions: 20 inches deep × 12 inches wide 

· Dead load: 0.82 kip/ft 

• Live load: 1.00 kip/ft 

· Concrete strength: 4.35 ksi 

· Concrete unit weight: 150 Ib/ft³ 

· Reinforcement: 3 #9 longitudinal bars 

· Steel yield strength: 60 ksi 

• Stirrups: 14 #3 bars spaced at 8.5 inches 


Fig. 6. Specifications for the evaluation of a simply-supported beam.



Table 4



Query classification and parameter extraction results.


<table><tr><td>Component</td><td colspan="4">Result</td></tr><tr><td rowspan="2">Task classification</td><td colspan="4">Evaluation</td></tr><tr><td colspan="4">The query involves analyzing an existing reinforced concrete beam design, including its geometry, loads, and material properties, which is sufficient for evaluation purposes.</td></tr><tr><td rowspan="8">Reasoning</td><td rowspan="2">Parameter category</td><td>Parameter</td><td>Value</td><td>Unit</td></tr><tr><td>Span length</td><td>25</td><td>ft</td></tr><tr><td rowspan="3">Geometry</td><td>Beam depth</td><td>20</td><td>in</td></tr><tr><td>Beam width</td><td>12</td><td>in</td></tr><tr><td>Dead load</td><td>0.82</td><td>kip/ft</td></tr><tr><td rowspan="2">Loads</td><td>Live load</td><td>1.00</td><td>kip/ft</td></tr><tr><td>Concrete strength</td><td>4.35</td><td>ksi</td></tr><tr><td>Concrete</td><td>Unit weight</td><td>150</td><td>lb/ft<eq>^{3}</eq></td></tr><tr><td rowspan="8">Extracted parameters</td><td rowspan="3"></td><td>Longitudinal diameter</td><td>1.128</td><td>in</td></tr><tr><td>Stirrup diameter</td><td>0.375</td><td>in</td></tr><tr><td>Longitudinal yield strength</td><td>60</td><td>ksi</td></tr><tr><td rowspan="5">Reinforcement</td><td>Stirrup yield strength</td><td>60</td><td>ksi</td></tr><tr><td>Number of longitudinal</td><td>3</td><td>-</td></tr><tr><td>Number of stirrup</td><td>14</td><td>-</td></tr><tr><td>Spacing of longitudinal</td><td>3</td><td>in</td></tr><tr><td>Spacing of stirrup</td><td>8.5</td><td>in</td></tr></table>


Serviceability assessment results.


<table><tr><td>Parameter type</td><td>Parameter</td><td>LLM result</td><td>Reference result</td><td>Reference to ACI 318-19</td></tr><tr><td rowspan="4">Modulus</td><td>Rupture modulus</td><td>494.66 psi (3.4 MPa)</td><td>494.66 psi (3.4 MPa)</td><td>Clause 19.2.3.1</td></tr><tr><td>Elastic modulus</td><td>3998.5 ksi (27,568.7 MPa)</td><td>3998.5 ksi (27,568.7 MPa)</td><td>Clause 19.2.2.1</td></tr><tr><td>Gross moment of inertial</td><td><eq>8000\text{ in}^4</eq> (<eq>3.33 \times 10^9</eq> mm<eq>^4</eq>)</td><td><eq>8000\text{ in}^4</eq> (<eq>3.33 \times 10^9</eq> mm<eq>^4</eq>)</td><td></td></tr><tr><td>Cracked moment of inertial</td><td><eq>3758.4\text{ in}^4</eq> (<eq>1.56 \times 10^9</eq> mm<eq>^4</eq>)</td><td><eq>3759.0\text{ in}^4</eq> (<eq>1.56 \times 10^9</eq> mm<eq>^4</eq>)</td><td></td></tr><tr><td rowspan="3">Moment of inertial</td><td>Effective moment of inertia for dead load</td><td><eq>4337.0\text{ in}^4</eq> (<eq>1.82 \times 10^9</eq> mm<eq>^4</eq>)</td><td><eq>4337.0\text{ in}^4</eq> (<eq>1.82 \times 10^9</eq> mm<eq>^4</eq>)</td><td></td></tr><tr><td>Effective moment of inertia for total load</td><td><eq>3811.3\text{ in}^4</eq> (<eq>1.59 \times 10^9</eq> mm<eq>^4</eq>)</td><td><eq>3812.0\text{ in}^4</eq> (<eq>1.59 \times 10^9</eq> mm<eq>^4</eq>)</td><td>Table 24.2.3.5</td></tr><tr><td>Cracking moment</td><td>32.98 kip-ft (44.7 kN·m)</td><td>32.98 kip-ft (44.7 kN·m)</td><td></td></tr><tr><td rowspan="3">Moment</td><td>Applied moment for dead load</td><td>64.06 kip-ft (86.9 kN·m)</td><td>64.06 kip-ft (86.9 kN·m)</td><td></td></tr><tr><td>Applied moment for total load</td><td>142.19 kip-ft (192.8 kN·m)</td><td>142.19 kip-ft (192.8 kN·m)</td><td></td></tr><tr><td>Deflection for dead load</td><td>0.416 in (10.57 mm)</td><td>0.416 in (10.57 mm)</td><td></td></tr><tr><td>Deflection</td><td>Combined long term deflection</td><td>1.480 in (37.60 mm)</td><td>1.465 in (37.21 mm)</td><td>Table 24.2.2</td></tr></table>

Supplementary Materials, showing the complete step-by-step process followed by the evaluation agent. Upon discovering that the beam exceeds long-term deflection limits, users can engage with the agent through natural language queries to explore the underlying causes and potential solutions. The framework addresses a key limitation of LLMs by performing code-compliant calculations. Precise computation often challenges LLMs, which struggle with logical consistency and reasoning required for complex processes [28]. 

## 4.3. Serviceability enhancement through expert consultation

After identifying the initial beam’s deflection issues, the system facilitates a collaborative analysis with the user through the agent. The agent responses are listed in Table A2 (Appendix). The process unfolds as follows: 

Inquiry 1: Why the beam satisfies the minimum height requirement but still fails the long-term deflection check? 

The LLM agent explains that while the beam height exceeds the code minimum, the calculated long-term deflection exceeds the allowable limit due to sustained loads, low reinforcement ratio, cracked section effects, and time-dependent behavior. The combined effect of live load and creep/shrinkage results in a total deflection of 1.48 in. (37.60 mm), which is greater than the allowable limit 1.25 in. (31.75 mm). 

The agent clarifies that the minimum height provisions provide only a preliminary guideline to avoid deflection calculations, but do not guarantee compliance with deflection limits for all loading conditions and reinforcement configurations. The agent also suggests several approaches to address the issue, such as increasing beam depth to enhance stiffness; increasing reinforcement to reduce cracking and increase the effective moment of inertia; using high-strength concrete to increase the modulus of elasticity; controlling creep and shrinkage through appropriate concrete design; and re-evaluating the applied loads to ensure they are not overestimated. 

Inquiry 2: Give me a specific plan for increasing the beam depth and validate it, remember to use the new effective depth. 

Based on the user’s selection of the beam depth increase strategy, the primary LLM agent develops a redesign plan to optimize the cross section of the beam for appropriate serviceability. The plan centers on increasing the beam height from 20 in. (508 mm) to 24 in. (610 mm) while maintaining the width and reinforcement layout. The agent provides a comprehensive procedure with calculations to ensure that the new cross section satisfies deflection requirements. 

The deflection calculations involve complex mechanics with multi ple variables, leading to numerical errors in the primary LLM’s response as shown in Table 7. The table reveals significant discrepancies in crit ical parameters: a 20 % overestimation of the cracking moment, an 8.3 % error in neutral axis depth calculation, and a 20.2 % underestimation of the effective moment of inertia for dead load. These errors lead to miscalculated deflection values that can result in incorrect design decisions. The verification LLM identifies these discrepancies and performs recalculations using calculator tool. The correction process maintains perfect accuracy for parameters like gross moment of inertia while rectifying the more complex calculations. 


Table 7


The integrator LLM then synthesizes these corrections into a coherent response, confirming that the new gross moment of inertia increases from 8000 $\mathrm { i n } ^ { 4 } ( 3 . 3 \overset { - } { 3 } \times 1 0 ^ { 9 } \mathrm { m m } ^ { 4 } )$ to $1 3 , 8 2 4 \ \mathrm { i n } ^ { 4 } \ ( 5 . 7 5 \times 1 0 ^ { 9 }$ $\mathrm { m m } ^ { 4 } ) _ { i }$ , significantly enhancing flexural stiffness. The properly calculated effective moment of inertia reduces deflections across all load cases. The accurate total long-term deflection is 1.04 in. (26.42 mm), which is lower than the allowable limit of 1.25 in. (31.75 mm). 

To quantify the benefits of the above verification process, two LLM configurations have been compared, which are a single-LLM approach (using the primary LLM without verification) and a three-LLM architecture (incorporating primary, verification, and integrator LLMs). The results are shown in Table 8, revealing significant differences in per formance metrics. 


Comparison of original and corrected deflection calculations


<table><tr><td>Parameter</td><td>Original result (Primary LLM)</td><td>Corrected result (Verification LLM)</td><td>Error (%)</td></tr><tr><td>Effective depth</td><td>21.56 in (548 mm)</td><td>21.56 in (548 mm)</td><td>0</td></tr><tr><td>Gross moment of inertial</td><td><eq>13,824 \text{ in}^{4}</eq><eq>(5.75 \times 10^{9} \text{ mm}^{4})</eq></td><td><eq>13,824 \text{ in}^{4}</eq><eq>(5.75 \times 10^{9} \text{ mm}^{4})</eq></td><td>0</td></tr><tr><td>Cracking moment</td><td>56.98 kip-ft(77.3 kN·m)</td><td>47.48 kip-ft(64.4 kN·m)</td><td>20.0</td></tr><tr><td>Neutral axis depth</td><td>7.82 in(199 mm)</td><td>7.22 in(183 mm)</td><td>8.3</td></tr><tr><td>Cracked moment of inertia</td><td><eq>6325.45 \text{ in}^{4}</eq><eq>(2.63 \times 10^{9} \text{ mm}^{4})</eq></td><td><eq>5978.0 \text{ in}^{4}</eq><eq>(2.49 \times 10^{9} \text{ mm}^{4})</eq></td><td>5.8</td></tr><tr><td>Effective moment of inertia for dead load</td><td><eq>7321.23 \text{ in}^{4}</eq><eq>(3.05 \times 10^{9} \text{ mm}^{4})</eq></td><td><eq>9174.14 \text{ in}^{4}</eq><eq>(3.82 \times 10^{9} \text{ mm}^{4})</eq></td><td>-20.2</td></tr><tr><td>Effective moment of inertia for total load</td><td><eq>6421.45 \text{ in}^{4}</eq><eq>(2.67 \times 10^{9} \text{ mm}^{4})</eq></td><td><eq>6270.30 \text{ in}^{4}</eq><eq>(2.61 \times 10^{9} \text{ mm}^{4})</eq></td><td>2.4</td></tr><tr><td>Dead load deflection</td><td>0.24 in(6.1 mm)</td><td>0.20 in(5.1 mm)</td><td>20.0</td></tr><tr><td>Total load deflection</td><td>0.62 in(15.7 mm)</td><td>0.64 in(16.3 mm)</td><td>-3.1</td></tr><tr><td>Live load deflection</td><td>0.48 in(12.2 mm)</td><td>0.44 in(11.2 mm)</td><td>9.1</td></tr><tr><td>Creep and shrinkage deflection</td><td>0.48 in(12.2 mm)</td><td>0.40 in(10.2 mm)</td><td>20.0</td></tr><tr><td>Total long-term deflection</td><td>1.10 in(27.9 mm)</td><td>1.04 in(26.4 mm)</td><td>5.8</td></tr></table>


Table 8



Comparison of LLM architectures.


<table><tr><td>Performance metric</td><td>Single-LLM</td><td>Three-LLM</td></tr><tr><td>Maximum calculation error</td><td>20.2 %</td><td>0 %</td></tr><tr><td>Response time</td><td>55 s</td><td>189 s</td></tr><tr><td>API cost</td><td>$0.003</td><td>$0.008</td></tr></table>

The single-LLM approach demonstrates faster response times and lower costs but exhibits critical limitations in accuracy, with a maximum error of 20.2 % for the effective moment of inertia. In contrast, the three-LLM architecture achieves high accuracy through its verification mechanism, but with slower response time and higher API cost. This trade-off between accuracy and efficiency highlights the value of the verification process in safety-critical applications. 

The LLM agent demonstrates robust engineering analysis in addressing the deflection problem, delivering solutions that adhere to ACI 318–19 with valid calculations. Its effectiveness stems from evaluation agent results, the code-based knowledge, and the calculator tool of the verification LLM. 

## 5. Implementation

To make the framework accessible to practitioners, an intuitive GUI was developed to facilitate applications while maintaining transparency. The interface features a design conversation panel and display results and calculation steps. As shown in Fig. 7, the Engineering Query section presents Case Study 1, where a user needs help designing a simply-supported reinforced concrete beam with specific material properties and loading conditions. 

Users can interact with the system via natural language queries, entering design requirements or evaluation requests in text. The system supports OCR-enhanced input, allowing users to use images of hand sketches. Users can upload detailed images, which the system can interpret and extract as design parameters. 

The interface is organized with two primary tabs: “Primary Query” for initial design or evaluation and “Further Inquiries” for follow-up questions and design refinement. This structure aligns with the workflow of the Expert Consultation agent, enabling seamless transitions 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-10-21/373b0a38-2fcf-4fbd-8f5c-effe78e1d2e1/a54bbf310911c080408f231c64eaf2769aeda7c276ce28ca2d092e5679841d31.jpg)



Fig. 7. Primary query of the structural engineering system.


between initial design and iterative refinement. The section titled “Key Takeaways and Recommendations” presents design decisions, including the adequate member size 20 in $\times \ 1 2$ in (305 mm × 508 mm), reinforcement detail 3#9 bars $A _ { s } = 2 . 8 6 9 \mathrm { i n } ^ { 2 } ( 1 8 5 0 \mathrm { m m } ^ { 2 } ) ,$ and shear reinforcement #3 stirrups@8.5 in (216 mm), totaling 14 stirrups. The system confirms code compliance and requirements for spacing, ductility $( \varepsilon _ { t } > 0 . 0 0 5 )$ , and shear, while also suggesting optimization opportunities such as relaxing stirrup spacing beyond the cutoff point 101.44 in (2577 mm). 

The right panel displays the “Tool Execution Status” with checkboxes indicating completed analyses including Member Sizing, Load Analysis, Structural Analysis, Flexural Design, and Shear Design. These checkboxes serve a critical error handling function, as if any tool fails to complete its analysis, the corresponding box remains unchecked, and the system immediately reports specific errors to prevent potentially unsafe designs. This robust error handling mechanism ensures that no design recommendations are provided when a calculation tool is compromised or returns invalid results. The “Final Verdict” declares the design as “structurally sound, code-compliant, and efficiently detailed”. 

The system features a “Save Design Case to Database” mechanism that enables users to preserve satisfactory design solutions, creating a comprehensive repository of validated engineering problem-solving patterns. This repository serves dual purposes: it functions as a prac tical reference library for future projects while simultaneously providing valuable training data for system enhancement. Users can quickly retrieve proven solutions for similar engineering challenges. The collected design cases provide essential data for fine-tuning the LLMs to better recognize patterns in engineering constraints and user prefer ences, transforming a static tool into an evolving system that become increasingly aligned with users’ engineering practices over time. 

As shown in Fig. 8, the “Further Inquiries” tab showcases the system’s response to a follow-up query about increased live load conditions. The interface demonstrates detailed calculation steps, starting with factored load computation $( w _ { u } = 0 . 9 8 4 + 2 . 4 = 3 . 3 8 4 \mathrm { k i p / f t } . $ (49.4 kN/m)). For the maximum moment calculation of the beam with uniform loads, the system applies the formula $M _ { \mathrm { { m a x } } } = ( w _ { u } L ^ { 2 } ) / 8 ,$ where the span length L is 25 ft. (7.6 m). 

The “Processing Options” panel provides user control over calculation validation modes. Users can enable “Use Calculation Validation” for heavy questions that require precise engineering calculations. Two validation modes are available for follow-up questions: “With Validation” uses a three-LLM architecture to validate calculations, providing higher accuracy but taking longer to process; “Without Validation” uses a single LLM for faster responses when precise calculations are not critical. The interface suggests toggling the “Use Calculation Validation” checkbox based on specific needs for each follow-up question, giving users control over the trade-off between computational accuracy and response time. 

![image](https://cdn-mineru.openxlab.org.cn/result/2026-10-21/373b0a38-2fcf-4fbd-8f5c-effe78e1d2e1/44bb00a5410a23efa53c244571fdcdb876bd019d5af918f153d88cc8b5ce1539.jpg)



Fig. 8. Validation options for follow-up queries in the structural engineering system.


It should be noted that this GUI is a prototype used to demonstrate the proposed multi-agent LLM framework in potential practice. To demonstrate its functionality and user interaction, a video is publicly accessible via the GitHub repository: https://github.com/JinxinDev/ LLM-Automated-RC-Beam-Design. The current version is not yet an industrial-grade product or a plugin for commercial software. In future work, this prototype will be developed to incorporate additional design cases and integrate with established software. 

## 6. Discussion

This section focuses on further discussing the proposed framework regarding its validation (Section 6.1), strengths (Section 6.2), and limitations (Section 6.3). The validation efforts involve a comprehensive evaluation through comparison with results from industry-standard software based on statistical metrics. 

## 6.1. Validation framework

Beyond individual case studies, comprehensive statistical validation was conducted to assess the framework’s performance against industrystandard structural analysis software (SAP2000). A set of 30 beams were designed using the proposed framework. The designs cover a diverse set of parameters, including concrete strengths ranging from 3.0 ksi (20.7 MPa) to 7 ksi (48.3 MPa), steel yield strengths from 60 ksi (413.4 MPa) to 80 ksi (551.6 MPa), dead loads from 0.6 kip/ft. (8.8 kN/m) to 1.5 kip/ ft. (21.9 kN/m), live loads from 0.75 kip/ft. (10.9 kN/m) to 1.75 kip/ft. (25.6 kN/m), and span lengths between 20 ft. (6.1 m) and 40 ft. (12.2 m), utilizing various sizes of reinforcing bars (longitudinal bars: #7 to #11, and stirrups: #3 to #5). 

The generated designs were subsequently validated using SAP2000, enabling quantification of uncertainty margins and statistical reliability assessment across multiple design parameters. All 30 beams designed using the proposed framework passed SAP2000 validation, confirming their code compliance and structural safety. The validation focused on four critical structural parameters: maximum moment, maximum shear force, required cross section area of longitudinal bars, and required $A _ { \nu } / s .$ To evaluate performance, the error metrics presented in Table 9 were employed. In the formulas, n represents the total number of cases, y<sub>i</sub> represents the results from SAP2000, and ˆy<sub>i</sub> represents the results from the proposed framework. 


Table 9



Comprehensive list of statistical quantitative indicators.


<table><tr><td>Abbreviation</td><td>Formula</td><td>Description</td></tr><tr><td>RMSE</td><td><eq>RMSE = \sqrt{\frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2}</eq></td><td>Root Mean Squared Error</td></tr><tr><td>MAE</td><td><eq>MAE = \frac{1}{n} \sum_{i=1}^{n} |y_i - \hat{y}_i|</eq></td><td>Mean Absolute Error</td></tr><tr><td>MAPE</td><td><eq>MAPE = \frac{100\%}{n} \sum_{i=1}^{n} \left| \frac{y_i - \hat{y}_i}{y_i} \right|</eq></td><td>Mean Absolute Percentage</td></tr><tr><td>R2</td><td><eq>R^2 = 1 - \frac{\sum_{i=1}^{n} (y_i - \hat{y}_i)^2}{\sum_{i=1}^{n} (y_i - \bar{y}_i)^2}</eq></td><td>Coefficient of Determination</td></tr><tr><td>MSE</td><td><eq>MSE = \frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2</eq></td><td>Mean Squared Error</td></tr><tr><td>MSLE</td><td><eq>MSLE = \frac{1}{n} \sum_{i=1}^{n} (\log(y_i + 1) - \log(\hat{y}_i + 1))^2</eq></td><td>Mean Squared Logarithmic Error</td></tr><tr><td>MaxEr</td><td><eq>MaxEr = \max(|y_i - \hat{y}_i|)</eq></td><td>Maximum Error</td></tr><tr><td>ExVar</td><td><eq>ExVar = 1 - \frac{Var(y_i - \hat{y}_i)}{Var(y_i)}</eq></td><td>Explained Variance Score</td></tr><tr><td>MedAE</td><td><eq>MedAE = median(|y_i - \hat{y}_i|)</eq></td><td>Median Absolute Error</td></tr><tr><td>MARE</td><td><eq>MARE = \frac{1}{n} \sum_{i=1}^{n} \left| \frac{y_i - \hat{y}_i}{y_i} \right|</eq></td><td>Mean Absolute Relative Error</td></tr><tr><td>MSRE</td><td><eq>MSRE = \frac{1}{n} \sum_{i=1}^{n} \left| \frac{y_i - \hat{y}_i}{y_i} \right|^2</eq></td><td>Mean Square Relative Error</td></tr><tr><td>RMSRE</td><td><eq>RMSRE = \sqrt{\frac{1}{n} \sum_{i=1}^{n} \left( \frac{y_i - \hat{y}_i}{y_i} \right)^2}</eq></td><td>Root Mean Squared Relative Error</td></tr><tr><td>RRMSE</td><td><eq>RRMSE = \frac{\sqrt{\frac{1}{n} \sum_{i=1}^{n} \left( \frac{y_i - \hat{y}_i}{y_i} \right)^2}}{\max(y_i) - \min(y_i)}</eq></td><td>Relative Root Mean Square Error</td></tr><tr><td>MBE</td><td><eq>MBE = \frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)</eq></td><td>Mean Bias Error</td></tr></table>

Table 10 presents the metrics that quantify deviations between the designs from the proposed framework and SAP2000. The results reveal consistent low errors across all parameters, with MAPE values below 3 % and high $\mathrm { R } ^ { 2 }$ values (0.97–1.00) indicating excellent correlation with industry-standard calculations. The slight positive MBE for moment and shear calculations (0.65 kip-ft (0.88 kN⋅m) and 0.03 kip (0.13 kN) respectively) represents a conservative tendency that enhances safety margins, while the negligible negative MBE for reinforcement area $( - 0 . 0 2 \mathrm { i n } ^ { 2 } ( - 1 2 . 9 0 \mathrm { m m } ^ { 2 } ) )$ has minimal practical impact. RMSE remain low across all parameters (maximum moment: 5.69 kip-ft (7.71 kN⋅m), maximum shear force: 0.20 kip (0.89 kN), required reinforcement: 0.10 $\mathrm { i n } ^ { 2 } ~ ( 6 4 . 5 2 ~ \mathrm { m m } ^ { 2 } )$ , required $A _ { \nu } / s \colon 0 . 0 0$ in (0.00 mm)), indicating deviations well within acceptable engineering tolerances and confirming that the framework produces reliable designs suitable for practical application. 

Hypothesis testing using paired t-tests was performed to compare the framework’s outputs and SAP2000 results (Table 11). The t-statistic is calculated as: 

$$
t = \frac {\overline {{d}}}{s _ {d} / \sqrt {n}}\tag{1}
$$

$$
\overline {{d}} = \frac {1}{n} \sum_ {i = 1} ^ {n} d _ {i}\tag{2}
$$

$$
s _ {d} = \sqrt {\frac {\sum_ {i = 1} ^ {n} (d _ {i} - \overline {{d}}) ^ {2}}{n - 1}}\tag{3}
$$

where $d _ { i } = { \hat { y } } _ { i } - y _ { i } .$ The null hypothesis $\left( H _ { 0 } \right)$ states that there is no significant difference between the framework’s predictions and SAP2000 results. The alternative hypothesis suggests that there is a significant difference. The statistical analysis failed to reject the null hypothesis for all four parameters at the 99 % confidence level, with p-values consistently above the significance threshold of 0.01. The p-value represents the probability of observing a t-statistic as extreme or more extreme than the one computed, assuming $H _ { 0 }$ is true: 

$$
p = P \big (\left| T _ {d f} \right| \geq | t | \big)\tag{4}
$$


Table 10



Errors of the designs obtained from the proposed framework and SAP2000.


<table><tr><td>Parameters</td><td>Maximum moment</td><td>Maximum shear force</td><td>Required longitudinal reinforcement area</td><td>Required <eq>A_{v}/s</eq></td></tr><tr><td>RMSE</td><td>5.69 kip-ft(7.71 kN·m)</td><td>0.20 kip(0.89 kN)</td><td><eq>0.10\ in^{2}\ (64.52\ mm^{2})</eq></td><td>0.00 in(0.00 mm)</td></tr><tr><td>MAE</td><td>2.56 kip-ft(3.47 kN·m)</td><td>0.06 kip(0.27 kN)</td><td><eq>0.05\ in^{2}\ (32.26\ mm^{2})</eq></td><td>0.00 in(0.00 mm)</td></tr><tr><td>MAPE</td><td>1.12 %</td><td>0.15 %</td><td>1.51 %</td><td>2.61 %</td></tr><tr><td><eq>R^{2}</eq></td><td>1.00</td><td>1.00</td><td>0.98</td><td>0.97</td></tr><tr><td>MSE</td><td>32.38 (kip-ft)<eq>^{2}</eq>(59.48 (kN·m)<eq>^{2}</eq>)</td><td><eq>0.04\ kip^{2}</eq>(0.18 kN<eq>^{2}</eq>)</td><td><eq>0.01\ in^{4}\ (4162.31\ mm^{4})</eq></td><td><eq>0.00\ in^{2}</eq>(0.00 mm<eq>^{2}</eq>)</td></tr><tr><td>MSLE</td><td>0.00</td><td>0.00</td><td>0.00</td><td>0.00</td></tr><tr><td>MaxEr</td><td>21.45 kip-ft(29.08 kN·m)</td><td>1.05 kip(4.67 kN)</td><td><eq>0.38\ in^{2}\ (245.16\ mm^{2})</eq></td><td>0.00 in</td></tr><tr><td>ExVar</td><td>1.00</td><td>1.00</td><td>0.99</td><td>0.98</td></tr><tr><td>MedAE</td><td>1.28</td><td>0.01</td><td>0.02</td><td>0.00</td></tr><tr><td>MARE</td><td>0.01</td><td>0.00</td><td>0.02</td><td>0.03</td></tr><tr><td>MSRE</td><td>0.00</td><td>0.00</td><td>0.00</td><td>0.00</td></tr><tr><td>RMSRE</td><td>0.02</td><td>0.01</td><td>0.03</td><td>0.05</td></tr><tr><td>RRMSE</td><td>0.01</td><td>0.00</td><td>0.03</td><td>0.05</td></tr><tr><td>MBE</td><td>0.65 kip-ft(0.88 kN·m)</td><td>0.03 kip(0.13 kN)</td><td><eq>-0.02\ in^{2}\ (-12.90\ mm^{2})</eq></td><td>0.00 in(0.00 mm)</td></tr></table>


Table 11



Error metrics for framework validation against SAP2000.


<table><tr><td>Parameters</td><td>t-statistics</td><td>p-values</td><td>95 % CI lower</td><td>95 % CI upper</td><td>Correlation coefficient</td></tr><tr><td>Maximum moment</td><td>-0.624</td><td>0.538</td><td>-2.27kip-ft(-3.80 kN·m)</td><td>1.49kip-ft(2.02 kN·m)</td><td>0.998</td></tr><tr><td>Maximum shear force</td><td>-0.855</td><td>0.400</td><td>-0.11kip(-0.49 kN)</td><td>0.04 kip(0.18 kN)</td><td>1.000</td></tr><tr><td>Required longitudinal reinforcement area</td><td>1.289</td><td>0.208</td><td>-0.01in2(-6.45 mm2)</td><td>0.06 in2(38.71 mm2)</td><td>0.993</td></tr><tr><td>Required <eq>A_{v}/s</eq></td><td>-2.483</td><td>0.019</td><td>0.0 in(0.0 mm)</td><td>0.0 in(0.0 mm)</td><td>0.988</td></tr></table>

where $T _ { d f }$ is a random variable following a t-distribution with $d f = n - 1$ degrees of freedom. This indicates that there is insufficient statistical evidence to conclude that the framework’s results differ significantly from those produced by SAP2000. The 95 % confidence intervals for the true mean difference $\mu _ { d }$ 

$$
\mathrm{CI} = \left[ \overline {{d}} - t _ {d f, 0. 9 7 5} ^ {*} \frac {s _ {d}}{\sqrt {n}}, \overline {{d}} + t _ {d f, 0. 9 7 5} ^ {*} \frac {s _ {d}}{\sqrt {n}} \right]\tag{5}
$$

where $t ^ { * } d f , 0 . 9 7 5$ is the critical value from the t-distribution for a 95 % confidence level. 

These intervals included or approached zero, further corroborating the framework’s accuracy. Additionally, correlation analysis revealed a strong correlation between the framework’s outputs and SAP2000 results across all parameters. Pearson correlation coefficient (r) was defined as: 

$$
r = \frac {\sum_ {i = 1} ^ {n} (\widehat {y} _ {i} - \overline {{\widehat {y}}}) (y _ {i} - \overline {{y}})}{\sqrt {\sum_ {i = 1} ^ {n} (\widehat {y} _ {i} - \overline {{\widehat {y}}}) ^ {2} \sum_ {i = 1} ^ {n} (y _ {i} - \overline {{y}}) ^ {2}}}\tag{6}
$$

where $\bar { y }$ and $\vec { y }$ are the means of the SAP2000 and the framework’s re sults, respectively. These coefficients exceeded 0.98 in all test cases. This indicates a strong positive linear correlation, meaning the framework’s results agreed with the SAP2000 results in a predictable linear way. 

Statistical validation results show that while small deviations exist, they fall within acceptable engineering tolerances and do not compromise structural safety or code compliance. The validation results bridge a gap in AI design tools by providing quantifiable confidence in reliability. The framework’s high correlation with industry-standard software, natural language interface and transparent reasoning, positions it as a valuable complement to traditional design workflows. 

Regarding the influence of input parameters on the design outputs, the framework’s approach is distinct from traditional “black-box” machine learning models where input importance and dependencies are often inferred statistically. The relationship between specific inputs and the key design outputs is direct and explicitly defined by established engineering equations: 

• Maximum design actions: The maximum factored moment $( M _ { u } )$ and shear force $( V _ { u } )$ are calculated using basic mechanics, e.g., $M _ { u } =$ $w _ { u } L ^ { 2 } / 8$ and $V _ { u } = w _ { u } L / 2$ for a uniformly loaded, simply supported beam, showing clear dependency on factored load $( w _ { u } )$ and span (L). 

• Required longitudinal reinforcement area (A ): This is determined by the formula $A _ { s } = M _ { u } / ( \phi f _ { v } ( d { \ : } - \ : a / 2 ) )$ , making its value directly dependent on $M _ { u }$ (and thus $w _ { u }$ and $L ) ,$ , steel yield strength $( f _ { y } )$ 

effective depth $( d ) ,$ , and indirectly on concrete strength (f<sub>c</sub>) through the depth of the compression block (a). 

• Required shear reinforcement $( A _ { \nu } / s ) { \mathrm { : } }$ This is calculated $A _ { \nu } / s = ( V _ { u @ d }$ $\phi V _ { c } ) / ( \phi f _ { y } d ) $ , clearly depending on the design shear force $( V _ { u @ d } ) _ { : }$ concrete shear capacity $( \phi V _ { c } ,$ which is a function of $f _ { c }$ and dimensions), and the yield strength of shear reinforcement $( f _ { y } )$ 

Given these explicit, formula-driven relationships, the “importance” and “dependen $\mathrm { c y } ^ { \mathrm { , , } }$ of inputs are transparent and directly ascertainable from engineering principles and code provisions. 

## 6.2. Strengths of proposed approach

The case studies and statistical analysis demonstrate the potential of the multi-agent LLM framework as a valuable complement to existing structural design workflows. To evaluate the practical impact of the proposed approach, Table 12 shows the comparison of key performance metrics for the proposed framework (implemented with DeepSeek-V3 or GPT-4o), SAP2000, and manual calculations. GPT-4o is included as an additional test to demonstrate the flexibility and adaptability of the framework. The results were identical between the DeepSeek-V3 and GPT-4o implementations: both specified a 12 in × 20 in (305 mm × 508 mm) beam with longitudinal bars of three #9 and shear reinforcement of 14 #3@8.5 in (216 mm). The calculated deflection values were nearly identical, with a dead load deflection of 0.416 in (10.57 mm) for both models and combined long-term deflections of 1.480 in (37.60 mm) for DeepSeek-V3 and 1.482 in (37.64 mm) for GPT-4o, respectively. This consistency occurs because the core engineering calculations are performed by deterministic code-compliant tools rather than the LLMs themselves. 

In the case study on design tasks, the system integrated natural language interaction with code-compliant calculations, producing design solutions that closely matched reference values. The system demonstrates remarkable efficiency advantages, reducing design time by about 90 % compared with manual methods while maintaining high accuracy. 

The multi-agent framework exhibits the ability to address both hallucination and calculation limitations through four mechanisms. First, by decomposing complex tasks into subtasks, each agent can focus on a narrowly defined responsibility where accuracy can be more easily verified. Second, specialized calculation agents can employ external tools to perform precise calculations, eliminating reliance on the LLM’s internal calculation abilities. Third, agents can implement codecompliant tools and calculation methods that directly incorporate established design standards and engineering principles, ensuring that designs inherently satisfy regulatory requirements rather than merely checking outputs after the fact. This approach guarantees that designs are generated following verified engineering procedures from the start, rather than attempting to catch errors afterward. Finally, transparent communication between agents creates reasoning that engineers can inspect to ensure reliability. 

The approach offers a different workflow for managing labor during the design process. Manual calculations require engineers to sequentially work through each step of analysis and design. Traditional software interfaces involve navigating multiple screens, inputting parameters across various forms, and interpreting the resulting outputs. The proposed approach allows engineers to input design requirements via natural language queries, receiving comprehensive solutions that include calculations and code references. While all approaches ultimately require the same engineering parameters to be specified, the natural language interface saves time spent navigating software interfaces. Engineers maintain responsibility for verifying results and making final design decisions regardless of the method used. 

The system’s ability to explain complex concepts was verified in the case study on evaluation tasks. The system demonstrated its potential as an educational or practical tool by explaining why a design solution that satisfies the minimum height requirement fails to pass deflection checks, followed by providing a valid design solution. The verification LLM identified and corrected calculation errors, addressing reliability con cerns that have limited the applications of LLMs. 


Table 12



Comparison of approaches for single reinforced concrete beam design.


<table><tr><td>Evaluation criterion</td><td>Manual approach</td><td>Specialized software</td><td>Proposed approach (DeepSeek-V3)</td><td>Proposed approach (GPT-4o)</td></tr><tr><td>Time efficiency</td><td>≈ 60 min per beam</td><td>≈ 10 min per beam</td><td>≈ 5 min per beam</td><td>≈ 1 min per beam</td></tr><tr><td>Accuracy</td><td>High</td><td>High</td><td>High</td><td></td></tr><tr><td>Labor intensity</td><td>High (continuous design and calculation effort)</td><td>Moderate (requires navigation through multiple input forms)</td><td colspan="2">Moderate (unified natural language input)</td></tr><tr><td>Verifiability</td><td>High (explicit calculations)</td><td>Moderate (transparent rule-based methods but with limited explanations)</td><td colspan="2">High (transparent calculations with code references)</td></tr><tr><td>Adaptability to code change</td><td>High (manual implementation)</td><td>Moderate (requires software updates)</td><td colspan="2">Moderate (modular tools update with consistent user interface)</td></tr><tr><td>Learning curve</td><td>High (structure analysis needed)</td><td>High (software training needed)</td><td colspan="2">Low (natural language interface)</td></tr><tr><td>Further assistance</td><td>Limited</td><td>None</td><td colspan="2">Comprehensive</td></tr><tr><td>Cost analysis</td><td>Variable (based on engineer salary)</td><td>N/A (Covered by license)</td><td>$0.007–0.009 per design (API cost)</td><td>$0.08–0.10 per design (API cost)</td></tr></table>

The framework and traditional software share similar requirements when adapting to code changes, as both need programming updates to their calculation components when design codes are revised. The key difference lies in the user interaction experience. In the proposed framework, the natural language interaction layer remains consistent even when the calculation modules are updated. This means users continue to interact through the same conversational interface regard less of technical changes to the calculation modules. Traditional software may require users to adapt to interface changes when major updates are implemented. 

This framework has been tested with two different LLM implementations: GPT-4o and DeepSeek-V3. Both implementations produced consistent technical results, as the deterministic calculation tools handle the calculations regardless of which LLM coordinates the process. The implementations showed different operational characteristics: GPT-4o completed the design task in approximately 1 min compared to Deep Seek-V3’s 5 min, while DeepSeek-V3 incurred lower API costs ($0.007–0.009 per design) than GPT-4o ($0.08–0.10 per design). This modularity allows organizations to select the appropriate LLM based on their priorities for speed or cost efficiency while maintaining identical technical output quality. 

Across all implementation scenarios, the integration of code compliance with LLM-generated explanations addresses a critical chal lenge in AI-powered structural design and evaluation. The proposed system augments traditional workflows by automating calculations while maintaining compliance with codes. The explicit presentation of design parameters, intermediate values, and final solutions allows users to verify each step, addressing concerns about reliability in safety critical use cases. 

## 6.3. Limitations and future research

The implementation of the framework focuses on RC beams, which serve as a demonstration of capabilities but represent only a small subset of structural elements. Extending the framework to more types of structural elements (e.g., slabs, columns, frames), which require different calculations and considerations will involve developing additional code-compliant tools and specialized agents rather than funda mentally altering the agent architecture. For instance, future work will consider concrete confinement effects, which are particularly critical for columns and other compression members, to enhance the accuracy and applicability of the framework for various structural components. The proposed framework’s core strength of having agents that know when and how to use these tools remains scalable. Future research will addres this limitation by expanding the framework for the other types of structural elements, enabling a move toward comprehensive building system design rather than isolated component analysis. 

While the framework improves efficiency compared with traditiona methods, the current three-LLM architecture introduces latency. This computational overhead, though necessary for reliability, presents opportunities for future efficiency improvements. One promising direction is the implementation of enhanced ReAct prompting techniques [40] with a single LLM. Although this approach is still premature due to context length limitations and calculation inconsistency, advancements in LLMs may overcome the challenges. This approach has the potential to improve the reliability of the verification system without the computational overhead of multiple model calls. Future research will continue exploring this balance between architectural complexity and performance as LLM technology evolves. 

Additionally, future work can leverage the data collection mechanism introduced in Section 5, which archives design cases validated through user satisfaction. This curated repository of successful engineering problem-solving patterns offers a potential resource for finetuning the underlying models to enhance system performance. 

Furthermore, the current approach uses separate agents for design and evaluation tasks. While this separation follows established engineering practice of dividing design creation from verification, the study has not empirically validated whether this multi-agent approach outperforms a unified agent handling both responsibilities. A key direction for future work is to conduct ablation studies, comparing the proposed multi-agent framework against a single-agent baseline to quantify the performance benefits of this framework and better understand the tradeoff. 

It is also important to note that the results still require verification by qualified engineers, particularly for safety-critical applications. The framework should be viewed as an assistant that accelerates workflows and reduces routine tasks rather than as a replacement for engineering judgment. Looking forward, the framework is not seeking to replace traditional structural software but rather to augment it. The LLM components themselves cannot perform complex analyses and calculations independently and require integration with established tools. Future development should focus on creating seamless connections with industry-standard software such as ETABS, SAP2000, CAD and BIM platforms, where the agents serve as the “brain” that orchestrates these specialized tools. 

The proposed framework functions as an intelligent interface between engineers and existing software. Engineers provide high-level instructions, and the LLM agents translate instructions into specific workflows across multiple software platforms and present comprehensive results for verification. This integration preserves the substantial investments made in established software while dramatically improving accessibility and efficiency. 

The path forward suggests a future where structural engineers spend less time on repetitive calculations and software operations, and more time applying their expertise to evaluate design alternatives, optimize solutions, and address unique challenges. As these technologies continue to mature, the vision encompasses a collaborative environment where human creativity and judgment are enhanced rather than replaced by AI capabilities. 

## 7. Conclusion

This paper presented a multi-agent LLM approach for automatic design or evaluation of code-compliant reinforced concrete structures. The performance of the approach was evaluated via two case studies on the design and evaluation of concrete beams. Based on the above in vestigations, the following conclusions were drawn: 

• The multi-agent LLM approach was effective in the task for design and evaluation of code-compliant reinforced concrete beams. The framework combined specialized LLM agents to execute structural design and evaluation tasks. Through a task-based division of responsibilities, each agent focused on its area of expertise, from initial query classification by the Task Dispatcher to specialized agents. These agents worked with a central Code-based Knowledge re pository that coordinates calculation tools and code requirements, ensuring designs adhere to regulatory standards. The Expert Consultation agent facilitated follow-up refinement, completing the coordination cycle. This organized approach allowed the system to maintain accuracy, verifiability, and code-compliance. 

• The framework demonstrated advantages compared to traditional methods in case studies. The framework reduced design time by about 90 % compared to manual approaches while maintaining calculation accuracy: (1) reinforcement area: 2.869 in<sup>2</sup> (1850 mm<sup>2</sup>) versus 2.872 in<sup>2</sup> (1853 mm<sup>2</sup>); (2) shear capacity: 41.30 ksi (183.7 kN) versus 41.79 ksi (185.9 kN). The modular architecture supported varying operational characteristics: GPT-4o completed designs within 1 min while DeepSeek-V3 used 5 min; yet DeepSeek-V3 offered lower API cost ($0.007–0.009) compared with GPT-4o ($0.08–0.10). 

• The graphical user interface made the proposed approach accessible to practitioners via natural language interaction and OCR-enhanced input. The implementation enabled iterative design refinement through conversation while maintaining transparency in calculations with code references, as demonstrated by optimizations like simplifying reinforcement from three #9 bars to two #11 bars and reducing long-term deflection by 30 %. This approach eliminated the steep learning curve associated with specialized software while providing comprehensive assistance for design optimization, validation, and code compliance verification. 

• The three-LLM architecture demonstrated a balance between accuracy, efficiency, code-compliance, and interpretability. When tested for deflection analysis, the verification mechanism successfully corrected errors in the calculation of effective moment of inertia. While the three-LLM approach increased response time (from 55 to 189 s) and API costs (from $0.003 to $0.008), it eliminated errors in safetyrelevant calculations, demonstrating the necessity of verification in structural engineering applications. 

• Statistical validation across 30 beam designs confirmed the frame work’s reliability with correlation coefficients exceeding 0.98 against industry-standard software SAP2000. Error metrics revealed high precision with MAPE values below 3 % for all parameters, including maximum moment (RMSE 5.69 kip-ft (7.72 kN⋅m)), maximum shear force (MAE 0.06 kip (0.27 kN)), and required rein forcement area (RMSE 0.10 in<sup>2</sup> (64.5 mm<sup>2</sup>)). These error values were within acceptable engineering tolerances and do not compromise structural safety or code compliance. 

Based on the above investigations, four recommendations are provided: (1) The proposed framework’s transparent reasoning ability can be used to demonstrate code-compliant design processes, and natural language can be used to scaffold learning while emphasizing verification. (2) The selection of LLM should leverage a strategic approach based on priorities: GPT-4o for time efficiency or DeepSeek-V3 for cost efficiency. (3) For complex designs with serviceability considerations, practitioners are suggested to employ the three-LLM architecture with verification, particularly for deflection analyses where single-LLM approaches showed high error rates. (4) Developers can prioritize integration with BIM and structural analysis software, positioning the multi agent system as an intelligent interface that enhances automation. 

The current implementation into reinforced concrete beams, while effective for demonstrating the capabilities of the proposed framework, has significant limitations in scope. It is believed that the framework is scalable to other structural elements (e.g., slabs, columns, frames) via the addition of specialized tools and agents rather than fundamental redesign. It is recommended to expand the capabilities to diverse structural elements beyond beams, reduce the computational overhead and latency of the current LLM architecture, leverage collected cases fo fine-tuning and performance enhancement, validate whether multiagent separation outperforms unified approaches, and create seamless integration with industry software, such as SAP2000, ETABS, and AutoCAD. 

The multi-agent LLM framework enables a paradigm where AI augments human expertise rather than replacing it, allowing engineers to focus on creative problem-solving and judgment while automating routine calculations with code compliance. A vision for future structural design and evaluation tasks involves a collaborative ecosystem where engineers spend less time on repetitive tasks and concentrate time on applying their knowledge and creativity to evaluate alternatives, optimize solutions, and address unique challenges. 

## CRediT authorship contribution statement

Jinxin Chen: Writing – original draft, Visualization, Software, Methodology, Investigation, Formal analysis, Data curation, Conceptualization. Yi Bao: Writing – review & editing, Validation, Supervision, Resources, Project administration, Methodology, Conceptualization. 

## Declaration of competing interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper. 


Table A1



Expert consultation responses for design optimization.


<table><tr><td>Further inquiry</td><td>Expert Consultation response</td></tr><tr><td></td><td rowspan="2">Reducing the cost of a reinforced concrete beam while maintaining the required moment and shear capacities involves optimizing the design and material usage. Here are several strategies to achieve this:1. Optimize Beam DimensionsAdjust Depth and Width: The beam&#x27;s depth and width can be optimized to reduce material usage while still meeting strength and deflection requirements. For example, increasing the depth slightly can reduce the required reinforcement area, potentially saving on steel costs.Use Standard Sizes: Designing beams to standard dimensions can reduce formwork costs and simplify construction.2. Optimize ReinforcementUse Higher-Grade Steel: Using higher-grade steel (e.g., Grade 75 instead of Grade 60) can reduce the required reinforcement area, leading to cost savings in steel and potentially reducing labor costs.Optimize Bar Sizes and Spacing: Use larger-diameter bars where possible to reduce the number of bars and simplify placement. Ensure that the spacing meets code requirements for crack control and shear capacity.Minimize Reinforcement: Ensure that the reinforcement provided is not significantly more than required by the design calculations. Avoid over-reinforcing, which increases costs without providing additional strength.3. Shear Reinforcement OptimizationUse Minimum Shear Reinforcement: Ensure that the shear reinforcement provided is the minimum required by code. Over-designing shear reinforcement can lead to unnecessary costs.Optimize Stirrup Spacing: Use the maximum allowable stirrup spacing to reduce the number of stirrups required. Ensure that the spacing meets code requirements for shear capacity and crack control.4. Material SelectionConcrete Strength: Use the minimum required concrete strength that meets the design requirements. Higher-strength concrete is more expensive and may not be necessary for all parts of the structure.Reinforcement Type: Consider using welded wire fabric or other types of reinforcement if they are more cost-effective for the specific application.5. Construction PracticesEfficient Formwork: Use reusable formwork systems to reduce costs. Efficient formwork design can also reduce labor costs.Batch Mixing: Optimize concrete mix designs to reduce waste and ensure that the mix meets the required strength without over-designing.6. Design ConsiderationsLoad Path Optimization: Ensure that the load path is efficient and that the beam is not over-designed for loads that are not present.Deflection Control: Ensure that the beam design meets deflection criteria without over-designing. Excessive depth or reinforcement to control deflection can increase costs.7. Alternative MaterialsFiber-Reinforced Concrete: In some cases, using fiber-reinforced concrete can reduce the need for shear reinforcement, leading to cost savings.Precast Concrete: Consider using precast concrete beams if they are more cost-effective for the project. Precast elements can reduce on-site labor and formwork costs.8. Value EngineeringReview Design: Conduct a value engineering review to identify areas where cost savings can be achieved without compromising structural integrity.Collaborate with Contractors: Work closely with contractors to identify cost-saving opportunities during construction.Using larger-diameter bars is an effective way to reduce costs by minimizing the number of bars, labor for placement, and tying. Below is a specific plan for implementing larger-diameter bars in the provided beam design while maintaining the required moment and shear capacities:Step 1: Evaluate Current ReinforcementCurrent Design: The beam uses three #9 bars <eq>A_s = 3.00 \text{ in}^2</eq> with a total area of steel of <eq>2.874 \text{ in}^2</eq>.Required Area of Steel: The design requires <eq>2.874 \text{ in}^2</eq> to resist the maximum moment of 201.88 kip-ft.Step 2: Check Feasibility of Larger BarsLarger Bar Options: Consider using two #11 bars <eq>A_s = 3.12 \text{ in}^2</eq> or two #10 bars <eq>A_s = 2.54 \text{ in}^2</eq>.Area Comparison:- Two #11 bars: <eq>2 \times 1.56 = 3.12 \text{ in}^2</eq>, (exceeds required <eq>A_s = 2.874 \text{ in}^2</eq>).- Two #10 bars: <eq>2 \times 1.27 = 2.54 \text{ in}^2</eq>, (slightly below required <eq>A_s = 2.874 \text{ in}^2</eq>.- Decision: Use two #11 bars because they provide sufficient area of steel (<eq>3.12 \text{ in}^2 &gt; 2.874 \text{ in}^2</eq>).Step 3: Verify Moment Capacity-Moment Capacity Check:- Calculate the depth of the compression block <eq>a</eq>:</td></tr><tr><td>In which way can we reduce cost while maintaining required capacities?</td></tr></table>

(continued on next page) 


Table A1 (continued )


<table><tr><td>Further inquiry</td><td>Expert Consultation response</td></tr><tr><td></td><td rowspan="3"><eq>a = \frac{A_{s}f_{y}}{0.85f_{c}b} = \frac{3.12 \times 60000}{0.85 \times 4350 \times 12} = 4.22</eq> in- Calculate the nominal moment capacity <eq>M_{n}</eq>:<eq>M_{n} = A_{s}f_{y}\left(d - \frac{a}{2}\right) = 3.12 \times 60000 \times \left(17.42 - \frac{4.22}{2}\right) = 238.74</eq> kip-ft- Factored moment capacity <eq>\phi M_{n}</eq>:<eq>\phi M_{n} = 0.9 \times 238.74 = 214.87</eq> kip-ft- Check:<eq>\phi M_{n} = 214.87</eq> kip-ft &gt; 201.88 kip-ft (OK).Step 4: Verify Shear Capacity- Shear Capacity: The shear design is independent of the flexural reinforcement. The existing stirrup design (#3 @ 8.5 in) remains valid.Step 5: Check Spacing and Clearance- Bar Diameter: #11 bars have a diameter of 1.41 in.- Clear Cover: 1.5 in. (as per design).- Stirrup Diameter: #3 stirrups have a diameter of 0.375 in.- Edge Distance:Edge distance = <eq>1.5 + 0.375 + \frac{1.41}{2} = 2.58</eq> in- Spacing Between Bars:Spacing = <eq>\frac{12.2 \times 2.58}{2.1} = 6.84</eq> in- Minimum Spacing Requirement:- ACI 318–19 requires a minimum spacing of 1.5 times the bar diameter or 1.5 in., whichever is greater.- For #11 bars: <eq>1.5 \times 1.41 = 2.12</eq> in.- Check: 6.84 in &gt;2.12 in (OK).Step 6: Update Reinforcement Layout- Final Layout:- Use two #11 bars at the bottom of the beam.- Maintain #3 stirrups @ 8.5 in. for shear reinforcement.- Ensure proper edge distance and spacing as calculated above.Step 7: Cost Comparison- Labor Savings:- Fewer bars reduce the time required for placement and tying.- Simplified layout reduces the risk of errors during construction.- Material Savings:- Two #11 bars (<eq>3.12 \text{ in }^{2}</eq>) provide slightly more steel than three #9 bars (<eq>3.00 \text{ in }^{2}</eq>), but the reduction in labor costs outweighs the minor increase in material cost.To ensure the beam remains tension-controlled when using two #11 bars, we need to verify that the net tensile strain <eq>\varepsilon_{t}</eq> in the extreme tension reinforcement is greater than or equal to 0.005 (as per ACI 318–19). This ensures ductile behavior and allows the use of the full strength reduction factor <eq>\phi = 0.9</eq>.Step-by-Step VerificationStep 1: Calculate the Depth of the Neutral Axis- Calculate the depth of the compression block:<eq>a = \frac{A_{s}f_{y}}{0.85f_{c}b} = \frac{3.12 \times 60000}{0.85 \times 4350 \times 12} = 4.22</eq> in- Calculate the depth of the neutral axis:<eq>c = \frac{a}{\beta_{1}} = \frac{4.22}{0.833} = 5.07</eq> inStep 2: Calculate the Net Tensile Strain- The net tensile strain is calculated using the strain compatibility relationship:<eq>\varepsilon_{t} = \frac{0.003 \times (17.42 - 5.07)}{5.07} = 0.0073</eq>Step 3: Verify Tension-Controlled Condition- ACI 318–19 Requirement: For a section to be tension-controlled, <eq>\varepsilon_{t} \geq 0.005</eq>- Check:<eq>\varepsilon_{t} = 0.0073 \geq 0.005</eq>- The beam is tension-controlled.Step 4: Confirm Strength Reduction Factor- For tension-controlled sections, <eq>\phi = 0.9</eq>- Since <eq>\varepsilon_{t} = 0.0073 \geq 0.005</eq>, the section qualifies for <eq>\phi = 0.9</eq>.Summary- Neutral Axis Depth: 5.07 in.- Net Tensile Strain: 0.0073.- Tension-Controlled Check: <eq>\varepsilon_{t} = 0.0073 \geq 0.005</eq> (OK).- Strength Reduction Factor: 0.9.By using two #11 bars, the beam remains tension-controlled, ensuring ductile behavior and allowing the use of the full strength reduction factor <eq>\phi = 0.9</eq>. This satisfies ACI 318–19 requirements and maintains the safety and performance of the beam.In a corrosive environment, the spacing between reinforcement bars must comply with stricter requirements to ensure durability and prevent corrosion-related issues. ACI 318–19 provides specific guidelines for reinforcement spacing in such environments, primarily in Chapter 20 (Durability Requirements) and Chapter 24 (Control of Cracking).Key Considerations for Corrosive Environments1. Clear Cover:- Increase the clear cover to reinforcement to protect against corrosion. ACI 318–19 Table 20.5.1.3.1 specifies (continued on next page)</td></tr><tr><td>If we use two #11 bars, how do we ensure the beam remains tension-controlled?</td></tr><tr><td>In a corrosive environment, does the current spacing between two #11 bars still satisfy the code compliance?</td></tr></table>


Table A1 (continued )


<table><tr><td>Further inquiry</td><td>Expert Consultation response</td></tr><tr><td></td><td>minimum cover requirements based on exposure conditions.- For beams exposed to weather or in contact with ground, the minimum clear cover is 2 in. for #6 through #18 bars.2. Maximum Bar Spacing:- ACI 318-19 Section 24.3.2 limits the maximum spacing of reinforcement to control crack width, which is critical in corrosive environments.- The maximum spacing is calculated based on the stress in the reinforcement and the clear cover.3. Crack Control:- Corrosive environments require tighter crack control to prevent the ingress of moisture and chlorides, which can accelerate corrosion.Step-by-Step Verification for Two #11 BarsStep 1: Check Clear CoverCurrent Clear Cover: 1.5 in.Required Clear Cover in Corrosive Environment: 2 in. (per ACI 318-19 Table 20.5.1.3.1 for beams exposed to weather or in contact with ground).Action: Increase the clear cover to 2 in.Step 2: Calculate Edge Distance-Bar Diameter (#11): 1.41 in.- Stirrup Diameter (#3): 0.375 in.- Edge Distance:Edge distance = 2.0 + 0.375 + <eq>\frac{1.41}{2}</eq> = 3.08 inStep 3: Calculate Spacing Between Bars- Beam Width: 12 in.- Number of Bars: 2.- Spacing Between Bars:Spacing = <eq>\frac{12 - 2 \times 3.08}{2 - 1}</eq> = 5.84 inStep 4: Verify Maximum Spacing for Crack Control- ACI 318-19 Section 24.3.2:- The maximum spacing of reinforcement closest to the tension face is:<eq>s_{max} = 15 \frac{40000}{f_s} - 2.5c_c = 15 \frac{40000}{0.67 \times 60000} - 2.5 \times 2 = 10 \text{ in} &lt; 12 \text{ in}</eq>- Check:- Provided spacing = 5.84 in.- Maximum allowable spacing = 10 in.- Conclusion: The spacing of 5.84 in. satisfies the maximum spacing requirement.Step 5: Verify Minimum Spacing- ACI 318-19 Section 25.2:- The minimum spacing between bars is the greatest of:1. 1.5 times the bar diameter 1.5 × 1.41 = 2.12 in.2. 1.5 in.3. 1.33 times the maximum aggregate size (assume 0.75 in., so 1.33× 0.75 = 1 in.- Controlling Value: 2.12 in.- Check:- Provided spacing = 5.84 in. &gt; 2.12 in. (OK).Summary of Compliance- Clear Cover: Increased to 2 in. (meets ACI 318-19 requirements for corrosive environments).- Spacing Between Bars: 5.84 in. (satisfies both maximum and minimum spacing requirements).- Crack Control: Spacing is within the allowable limit for crack control in corrosive environments.Recommendations1. Increase Clear Cover: Use 2 in. of clear cover to meet durability requirements.2. Maintain Spacing: The current spacing of 5.84 in. between two #11 bars is acceptable and complies with ACI 318-19 for corrosive environments.3. Use Corrosion-Resistant Materials: Consider using epoxy-coated or stainless steel reinforcement for additional protection in highly corrosive environments.By following these steps, the beam design with two #11 bars will remain code-compliant in a corrosive environment while ensuring durability and performance.</td></tr></table>


Table A2



Expert consultation responses for serviceability enhancement.


<table><tr><td>Further inquiry</td><td>Expert Consultation response</td></tr><tr><td>Why the beam satisfies the minimum height requirement but still fails the long-term deflection check?</td><td>The beam satisfies the minimum height requirement because the minimum depth requirement (e.g., <eq>h \geq \frac{L}{16}</eq> for simply supported beams) is a simplified rule to ensure that the beam has sufficient stiffness to avoid excessive deflection under typical loading conditions. However, this rule does not account for all factors that influence long-term deflection, such as creep and shrinkage, which are time-dependent effects.Key Reasons for Failing the Long-Term Deflection Check:1. Creep and Shrinkage Effects:- Concrete undergoes long-term deformation due to creep (time-dependent deformation under sustained load) and shrinkage (volume reduction due to drying). These effects are not considered in the minimum depth requirement but are critical for long-term deflection calculations.</td></tr></table>

(continued on next page) 


Table A2 (continued )


<table><tr><td>Further inquiry</td><td>Expert Consultation response</td></tr><tr><td></td><td rowspan="2">- In your case, the time-dependent multiplier <eq>\lambda_{\Delta} = 2.0</eq> significantly increases the dead load deflection over time.The creep and shrinkage deflection <eq>\Delta_{cs} = 0.8312</eq> in is a major contributor to the total long-term deflection.2. Combined Deflection:- The total long-term deflection <eq>(\Delta_{total})_{It} = 1.8956</eq> in exceeds the allowable limit of <eq>\frac{L}{240} = 1.25</eq> in. This is because the combined effect of live load deflection <eq>\Delta_{II} = 0.6488</eq> in and creep/shrinkage deflection <eq>\Delta_{cs} = 0.8312</eq> in results in a total deflection of 1.48 in, which is greater than the limit.3. Minimum Depth Requirement is Not Sufficient:- The minimum depth requirement is a conservative rule of thumb and does not guarantee compliance with serviceability limits like deflection. It only ensures that the beam is not excessively shallow, which could lead to immediate deflection issues.4. Reinforcement Ratio and Stiffness:- The beam&#x27;s stiffness depends on the effective moment of inertia <eq>I_e</eq>, which is influenced by the reinforcement ratio and cracking. If the reinforcement ratio is low, the beam may crack more, reducing its stiffness and increasing deflection.How to Address the Issue:1. Increase Beam Depth:- Increasing the beam depth h will increase the gross moment of inertia <eq>I_g</eq> and reduce deflection. This is the most effective way to improve stiffness.2. Increase Reinforcement:- Adding more reinforcement (e.g., increasing <eq>A_s</eq> will reduce cracking and increase the effective moment of inertia <eq>I_o</eq>, thereby reducing deflection.3. Use Higher-Strength Concrete:- Higher-strength concrete <eq>f_c</eq> increases the modulus of elasticity <eq>E_c</eq> and reduces deflection.4. Control Creep and Shrinkage:- Use low-shrinkage concrete mixes or additives to reduce long-term deformation. Proper curing can also minimize shrinkage.5. Revise Load Assumptions:- Re-evaluate the applied loads (dead and live) to ensure they are not overestimated. Reducing the loads will directly reduce deflection.Summary:The beam satisfies the minimum depth requirement because it is a simplified rule, but it fails the long-term deflection check due to the combined effects of live load deflection, creep, and shrinkage. To address this, you can increase the beam depth, add more reinforcement, or use higher-strength concrete to improve stiffness and reduce deflection.To address the long-term deflection issue, we will increase the beam depth and recalculate the deflection using the new effective depth. Below is the plan and validation, with both original and corrected calculations shown for transparency.Plan to Increase Beam Depth1. Current Beam Dimensions:- Width h: 12 in- Height h: 20 in- Effective depth d: 17.56 in2. Proposed New Beam Dimensions:- Increase height h to 24 in.- New effective depth <eq>d_{new}</eq>: <eq>h_{new} \cdot 2.44 = 24 - 2.44 = 21.56</eq> in.3. Recalculate Key Parameters:- Gross moment of inertia: <eq>I_g = \frac{bh^3}{12}</eq>- Cracking moment: <eq>M_{cr} = \frac{f_I_g}{y_t}</eq>- Cracked moment of inertia:<eq>I_{cr} = \frac{b(kd)^3}{3} + nA_s(d - kd)^2</eq>- Effective moment of inertia <eq>I_e = I_{cr} + (I_g - I_{cr}) \left( \frac{M_{cr}}{M_a} \right)^3</eq>- Deflection: <eq>\Delta = \frac{5wL^4}{384EI}</eq>4. Recalculate Long-Term Deflection:- Dead load deflection <eq>\Delta_{dl}</eq>- Live load deflection <eq>\Delta_{ll}</eq>- Creep and shrinkage deflection <eq>\Delta_{cs}</eq>- Total long-term deflection <eq>\Delta_{lt}</eq>Validation with New Beam Depth1. New Gross Moment of Inertia Ig:<eq>I_g = \frac{bh^3}{12} = \frac{12 \times 24^3}{12} = 13824 \text{ in }^4</eq>2. New Cracking Moment <eq>M_{cr}</eq>:<eq>M_{cr} = \frac{f_I_g}{y_t} = \frac{496.66 \times 13824}{12} = 47.48 \text{ kip-ft}</eq>3. New Cracked Moment of Inertia Icr:- Neutral axis depth<eq>kd = \frac{-1 + \sqrt{1 + 2Bd}}{B} = \frac{-1 + \sqrt{1 + 2 \times 21.56 \times 0.55}}{0.55} = 7.22 \text{ in}</eq>- Cracked moment of inertia:<eq>I_{cr} = \frac{12 \times 7.22^3}{3} + 7.25 \times 3 \times (21.56 - 7.22)^2 = 5978.0 \text{ in }^4</eq>(continued on next page)</td></tr><tr><td>Give me a specific plan for increasing the beam depth and validate it, remember to use new effective depth.</td></tr></table>

Table A2 (continued ) 

<table><tr><td>Further inquiry</td><td>Expert Consultation response</td></tr><tr><td></td><td>4. New Effective Moment of Inertia <eq>Ie</eq>:- For dead load <eq>Ma = 64.06</eq> kip-ft:<eq>I_e = 5978.0 + (13824 - 5978.0)\left(\frac{47.49}{64.06}\right)^3 = 9174.14 \text{ in}^4</eq>- For total load <eq>Ma = 142.19</eq> kip-ft:<eq>I_e = 5978.0 + (13824 - 5978.0)\left(\frac{47.49}{142.19}\right)^3 = 6270.3 \text{ in}^4</eq>5. New Deflections:- Dead load deflection:<eq>\Delta_{dl} = \frac{5wL^4}{384E_cI_e} = \frac{5 \times 0.82 \times 83.3 \times 300^4}{384 \times 3998484.87 \times 9174.14} = 0.20 \text{ in}</eq>- Total load deflection:<eq>\Delta_{total} = \frac{5wL^4}{384E_cI_e} = \frac{5 \times 0.82 \times 83.3 \times 300^4}{384 \times 3998484.87 \times 6270.31} = 0.64 \text{ in}</eq>- Live load deflection:<eq>\Delta_{ll} = \Delta_{total} - \Delta_{dl} = 0.64 - 0.20 = 0.44 \text{ in}</eq>6. New Long-Term Deflection:- Creep and shrinkage deflection:<eq>\Delta_{cs} = \lambda_\Delta \Delta_{dl} = 2 \times 0.20 = 0.40 \text{ in}</eq>- Total long-term deflection:<eq>(\Delta_{total})_{lt} = \Delta_{dl}(1 + \lambda_\Delta) + \Delta_{ll} = 0.20(1 + 2.0) + 0.44 = 1.04 \text{ in}</eq>7. Check Against Allowable Deflection:- Allowable deflection <eq>\frac{L}{240}</eq>: 1.25 in- Total long-term deflection: 1.04 in- Result:1.04 in&lt;1.25 in→ PASS</td></tr></table>

## Appendix B. Supplementary data

Supplementary data to this article can be found online at https://doi.org/10.1016/j.autcon.2025.106331. 

## Data availability

Data will be made available on request. 

## References



[1] M.N. Hassoun, A. Al-Manaseer, Structural Concrete: Theory and Design, John Wiley Sons, 2020. ISBN: 978-1-119-60511-9. 





[2] A. Borrmann, M. Konig, ¨ C. Koch, J. Beetz, Building information modeling, in: Why? What? How?, Springer International Publishing, 2018, pp. 1–24, https://doi.org/ 10.1007/978-3-319-92862-3_1. 





[3] E.U. Syed, K.M. Manzoor, Analysis and design of buildings using Revit and ETABS software, Mater. Today Proc. 65 (2022) 1478 1485, https://doi.org/10.1016/j. matpr.2022.04.463. 





[4] H. Li-Jeng, S. Hong-Jie, Seismic response analysis of tower crane using SAP2000, Proc. Eng. 79 (2014) 513–522, https://doi.org/10.1016/j.proeng.2014.06.374. 





[5] J.L. Encarnacao, R. Lindner, E.G. Schlechtendahl, Computer Aided Design: Fundamentals and System Architectures, Springer Science & Business Media, 2012, https://doi.org/10.1007/978-3-642-84054-8. 





[6] Y. Fei, W. Liao, S. Zhang, P. Yin, B. Han, P. Zhao, X. Chen, X. Lu, Integrated schematic design method for shear wall structures: a practical application of generative adversarial networks, Buildings 12 (9) (2022) 1295, https://doi.org 10.3390/buildings12091295. 





[7] Z. He, Y.H. Wang, J. Zhang, Generative structural design integrating BIM and diffusion model, arXiv preprint arXiv:2311.04052, 2023, https://doi.org/ 10.48550/arXiv.2311.04052. 





[8] F. Kazemi, N. Asgarkhani, R. Jankowski, Machine learning-based seismic response and performance assessment of reinforced concrete buildings, Arch. Civil Mech. Eng. 23 (2) (2023) 94, https://doi.org/10.1007/s43452-023-00631-9. 





[9] H. Sun, H.V. Burton, H. Huang, Machine learning applications for building structural design and performance assessment: state-of-the-art review, J. Build. Eng. 33 (2021) 101816, https://doi.org/10.1016/j.jobe.2020.101816. 





[10] J. Ferreiro-Cabello, E. Fraile-Garcia, E.M. de Pison Ascacibar, F.J. Martinez-de-Pison, Metamodel-based design optimization of structural one-way slabs based on deep learning neural networks to reduce environmental impact, Eng. Struct. 155 (2018) 91–101, https://doi.org/10.1016/j.engstruct.2017.11.005. 





[11] F. Liu, X. Jiang, X. Wang, L. Wang, Machine learning-based design and optimization of curved beams for multistable structures and metamaterials, Extreme Mech. Lett. 41 (2020) 101002, https://doi.org/10.1016/j. eml.2020.101002. 





[12] F. Kazemi, N. Asgarkhani, R. Jankowski, Optimization-based stacked machine learning method for seismic probability and risk assessment of reinforced concrete 





shear walls, Expert Syst. Appl. 255 (2024) 124897, https://doi.org/10.1016/j eswa.2024.124897. 





[13] F. Kazemi, N. Asgarkhani, R. Jankowski, Machine learning-based seismic fragility and seismic vulnerability assessment of reinforced concrete structures, Soil Dyn Earthq. Eng. 166 (2023) 107761, https://doi.org/10.1016/j.soildyn.2023.107761. 





[14] P. Zhao, W. Liao, H. Xue, X. Lu, Intelligent design method for beam and slab of shear wall structure based on deep learning, J. Build. Eng. 57 (2022) 104838, https://doi.org/10.1016/j.jobe.2022.104838. 





[15] Y. Zhou, H. Leng, S. Meng, H. Wu, Z. Zhang, StructDiffusion: end-to-end intelligent shear wall structure layout generation and analysis using diffusion model, Eng Struct. 309 (2024) 118068, https://doi.org/10.1016/j.engstruct.2024.118068. 





[16] C. Rudin, Stop explaining black box machine learning models for high stake decisions and use interpretable models instead, Nat. Mach. Intell. 1 (5) (2019) 206 215, https://doi.org/10.1038/s42256-019-0048-x. 





[17] G.S. Handelman, H.K. Kok, R.V. Chandra, A.H. Razavi, S. Huang, M. Brooks, M. J. Lee, H. Asadi, Peering into the black box of artificial intelligence: evaluation metrics of machine learning methods, Am. J. Roentgenol. 212 (1) (2019) 38–43, https://doi.org/10.2214/AJR.18.20224. 





[18] M.Z. Naser, S. Thai, H.T. Thai, Evaluating structural response of concrete-filled steel tubular columns through machine learning, J. Build. Eng. 34 (2021) 101888, https://doi.org/10.1016/j.jobe.2020.101888. 





[19] X.Y. Zhao, J.X. Chen, B. Wu, An interpretable ensemble-learning-based open source model for evaluating the fire resistance of concrete-filled steel tubular columns, Eng. Struct. 270 (2022) 114886, https://doi.org/10.1016/j. engstruct.2022.114886. 





[20] J. Chen, Y. Bao, Effect of dataset representation bias on generalizability of machine learning models in predicting flexural properties of ultra-high-performance concrete (UHPC) beams, Eng. Struct. 326 (2025) 119508, https://doi.org/ 10.1016/j.engstruct.2024.119508. 





[21] J. Ferreiro-Cabello, F.J. Martinez-de-Pison, E. Fraile-Garcia, A. Pernia-Espinoza, J. Divason, ´ Intelligent sensor software for robust and energy-sustainable decisionmaking in welding of steel reinforcement for concrete, Sensors 25 (1) (2024) 28, https://doi.org/10.3390/s25010028. 





[22] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A.N. Gomez, Ł. Kaiser, I. Polosukhin, Attention is all you need, Adv. Neural Inf. Proces. Syst. 30 (2017), https://doi.org/10.48550/arXiv.1706.03762. 





[23] S. Qin, H. Guan, W. Liao, Y. Gu, Z. Zheng, H. Xue, X. Lu, Intelligent design and optimization system for shear wall structures based on large language models and generative artificial intelligence, J. Build. Eng. 95 (2024) 109996, https://doi.org 10.1016/iiobe 2024.109996 





[24] X. Xue, J. Zhang, Y. Chen, Question-answering framework for building codes using fine-tuned and distilled pre-trained transformer models, Autom. Constr. 168 (2024) 105730, https://doi.org/10.1016/j.autcon.2024.105730. 





[25] H. Pu, X. Yang, J. Li, R. Guo, AutoRepo: a general framework for multimodal LLMbased automated construction reporting, Expert Syst. Appl. 255 (2024) 124601, https://doi.org/10.1016/j.eswa.2024.124601. 





[26] S. Meng, Y. Zhou, Q. Zheng, B. Liao, M. Chang, T. Zhang, A. Djerrad, SeisGPT: A Physics-Informed Data-Driven Large Model for Real-Time Seismic Response Prediction, arXiv preprint arXiv:2410.20186, 2024, https://doi.org/10.48550/ arXiv.2410.20186. 





[27] J.Y. Yao, K.P. Ning, Z.H. Liu, M.N. Ning, Y.Y. Liu, L. Yuan, Llm lies: hallucinations are not bugs, but features as adversarial examples, arXiv preprint arXiv: 2310.01469, 2023, https://doi.org/10.48550/arXiv.2310.01469. 





[28] L. Huang, W. Yu, W. Ma, W. Zhong, Z. Feng, H. Wang, Q. Chen, W. Peng, X. Feng, B. Qin, T. Liu, A survey on hallucination in large language models: principles, taxonomy, challenges, and open questions, ACM Trans. Inf. Syst. 43 (2) (2025) 1–55, https://doi.org/10.1145/3703155. 





[29] Z. Yuan, H. Yuan, C. Tan, W. Wang, S. Huang, How well do large language models perform in arithmetic tasks?, arXiv preprint arXiv:2304.02015, 2023, https://doi. org/10.48550/arXiv.2304.02015. 





[30] W. Zhang, C. Wan, Y. Zhang, Y.M. Cheung, X. Tian, X. Shen, J. Ye, Interpreting and improving large language models in arithmetic calculation, arXiv preprint arXiv: 2409.01659, 2024, https://doi.org/10.48550/arXiv.2409.01659. 





[31] X. Dong, X. Zhang, W. Bu, D. Zhang, F. Cao, A survey of LLM-based agents: theories, technologies, applications and suggestions, in: 2024 3rd International Conference on Artificial Intelligence, Internet of Things and Cloud Computing Technology (AIoTC), IEEE, 2024, September, pp. 407–413, https://doi.org 10.1109/AIoTC63215.2024.10748304. 





[32] J. Xie, K. Zhang, J. Chen, T. Zhu, R. Lou, Y. Tian, Y. Xiao, Y. Su, Travelplanner: a benchmark for real-world planning with language agents, arXiv preprint arXiv: 2402.01622, 2024, https://doi.org/10.48550/arXiv.2402.01622. 





[33] C. Gan, Q. Zhang, T. Mori, Application of llm agents in recruitment: a novel framework for resume screening, arXiv preprint arXiv:2401.08315, 2024, https:/ doi.org/10.48550/arXiv.2401.08315. 





[34] StructurePoint, Simply Supported Reinforced Concrete Beam Analysis and Design (ACI 318–14), Available at: https://structurepoint.org/publication/pdf/Simply% 20Supported%20Reinforced%20Concrete%20Beam%20Analysis%20and% 20Design%20(ACI%20318-14).pdf, 2021. 





[35] A. Liu, B. Feng, B. Xue, B. Wang, B. Wu, C. Lu, C. Zhao, C. Deng, C. Zhang, C. Ruan, D. Dai, Deepseek-v3 technical report, arXiv preprint arXiv:2412.19437, 2024, https://doi.org/10.48550/arXiv.2412.19437. 





[36] T. Gao, J. Jin, Z.T. Ke, G. Moryoussef, A Comparison of DeepSeek and Other LLMs, arXiv preprint arXiv:2502.03688, 2025, https://doi.org/10.48550 arXiv.2502.03688. 





[37] American Concrete Institute, Building Code Requirements for Structural Concrete (ACI 318–19), American Concrete Institute, Farmington Hills, MI, 2019. ISBN: 9781641950565. 





[38] D.C. Feng, W.J. Wang, S. Mangalathu, G. Hu, T. Wu, Implementing ensemble learning methods to predict the shear strength of RC deep beams with/without web reinforcements, Eng. Struct. 235 (2021) 111979, https://doi.org/10.1016/j. engstruct.2021.111979. 





[39] N.A. Nariman, K. Hamdia, A.M. Ramadan, H. Sadaghian, Optimum design of flexural strength and stiffness for reinforced concrete beams using machine learning, Appl. Sci. 11 (18) (2021) 8762, https://doi.org/10.3390/app11188762 





[40] M.S. Sandeep, K. Tiprak, S. Kaewunruen, P. Pheinsusom, W. Pansuk, Shear strength prediction of reinforced concrete beams using machine learning, in: Structures vol. 47, Elsevier, 2023, January, pp. 1196–1211, https://doi.org/10.1016/j. istruc.2022.11.140. 

