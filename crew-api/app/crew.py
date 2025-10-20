import pathlib
# from dotenv import load_dotenv
from .agents import planning_agent, script_agent, evaluation_agent, image_agent, video_agent, audio_agent, editor_agent
from .tasks import build_crew, run_pipeline
from .tools.idea_tools import generate_ad_idea
from dotenv import load_dotenv
load_dotenv()

# Prevent CrewAI from requiring a real OpenAI key
import os
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "unused"
def load_text(path):
    return pathlib.Path(path).read_text(encoding="utf-8")

def run(product_name, product_desc,current_run_id):


    # Load prompts
    script_prompt = load_text(os.path.join(os.path.dirname(__file__), "prompts/script_prompt.md"))
    eval_rubric   = load_text(os.path.join(os.path.dirname(__file__), "prompts/eval_rubric.md"))
    idea_prompt   = load_text(os.path.join(os.path.dirname(__file__), "prompts/idea_prompt.md"))

    
    chosen_idea = generate_ad_idea(product_name, product_desc, idea_prompt)

    # Agents: no LLM objects needed because tools call Bedrock directly
    planner = planning_agent()
    s_agent = script_agent()       # llm optional
    e_agent = evaluation_agent()   # llm optional
    i_agent = image_agent()
    v_agent = video_agent()        # llm optional
    a_agent = audio_agent()
    ed_agent = editor_agent()

    crew = build_crew(planner, s_agent, e_agent, i_agent, v_agent, a_agent, ed_agent)

    prompts = {"script": script_prompt, "rubric": eval_rubric}

    result = run_pipeline(planner, s_agent, e_agent, i_agent, v_agent, a_agent, ed_agent,
                          prompts, product_name, product_desc, chosen_idea,current_run_id)
    result["idea_used"] = chosen_idea
    print("Pipeline result:", result)

    return result
