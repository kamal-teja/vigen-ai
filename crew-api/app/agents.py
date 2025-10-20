
from crewai import Agent

def _make_agent(**kwargs):
    # Drop llm key if it's None to avoid crewai expecting an LLM instance
    if "llm" in kwargs and kwargs["llm"] is None:
        kwargs.pop("llm")
    return Agent(**kwargs)

# Planning agent: no LLM
def planning_agent():
    return _make_agent(
        role="Planning Agent",
        goal="Decide pipeline order, track artifacts, and call agents at the right time.",
        backstory="A deterministic coordinator that does not use an LLM.",
        allow_delegation=False,
        verbose=True,
    )

def script_agent(llm=None):
    return _make_agent(
        role="Script Generation",
        goal="Generate a crisp, 60s ad script as strict JSON.",
        backstory="Award-winning copywriter and director.",
        verbose=True,
        llm=llm
    )

def evaluation_agent(llm=None):
    return _make_agent(
        role="Script Evaluator",
        goal="Evaluate the script by rubric and decide approve/revise.",
        backstory="Ad QA specialist.",
        verbose=True,
        llm=llm
    )

def image_agent():
    return _make_agent(
        role="Image Generation",
        goal="Create one key-frame image per scene using Nova Canvas.",
        backstory="Visual designer specialized in key frames.",
        verbose=True,
    )

def video_agent(llm=None):
    return _make_agent(
        role="Video Generation",
        goal="Generate one short clip per scene using Nova Reel or Kling.",
        backstory="Motion designer.",
        verbose=True,
        llm=llm
    )

def audio_agent():
    return _make_agent(
        role="Audio Generation",
        goal="Generate dialogue voiceovers with Amazon Polly.",
        backstory="Voice producer.",
        verbose=True,
    )

def editor_agent():
    return _make_agent(
        role="Video Editor",
        goal="Mux per-scene audio over video in MediaConvert and deliver final output.",
        backstory="Finishing editor.",
        verbose=True,
    )
