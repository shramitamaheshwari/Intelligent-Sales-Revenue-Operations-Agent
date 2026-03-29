from crewai.flow.flow import Flow, start, listen, or_
from crewai.flow.human_feedback import human_feedback, HumanFeedbackResult
from crewai import Agent, Task, Crew

from agents.analyst_agent import AnalystAgentBuilder
from agents.copywriter_agent import CopywriterAgentBuilder

sentiment_agent = AnalystAgentBuilder.build_agent()
copywriting_agent = CopywriterAgentBuilder.build_agent()

class RevenueRecoveryFlow(Flow):
    
    @start()
    def analyze_account_health(self):
        # Trigger predictive models from Pillar 1 & 2
        print("Analyzing CRM telemetry and recent email sentiment...")
        return "Churn Risk: High. Competitor 'AcmeCorp' mentioned in email. Usage dropped by 45% in 72 hours."

    @listen("analyze_account_health")
    def draft_recovery_play(self, context):
        print("Drafting recovery play based on psychological frameworks...")
        # Delegation to the specialized Crew for drafting
        drafting_task = Task(
            description=f"Draft a recovery email based on this account context: {context}",
            expected_output="A well-crafted recovery email addressing the risk context.",
            agent=copywriting_agent
        )
        crew = Crew(agents=[copywriting_agent], tasks=[drafting_task])
        draft = crew.kickoff()
        self.state['current_draft'] = str(draft)
        return self.state['current_draft']

    # HITL Gate: Interprets free-form human feedback into discrete routing states
    @human_feedback(
        message="Review the AI-drafted recovery email. Do you approve, reject, or need specific revisions?",
        emit=["approved", "rejected", "needs_revision"],
        llm="groq/llama3-8b-8192", # Lightweight free router model for structured output parsing
        default_outcome="needs_revision"
    )
    # The or_ operator enables the self-healing revision loop
    @listen(or_("draft_recovery_play", "needs_revision"))
    def review_loop(self, context):
        if isinstance(context, HumanFeedbackResult):
            print(f"Refining draft based on AE feedback: {context.feedback}")
            revision_task = Task(
                description=f"Revise this draft: {self.state['current_draft']}. Human feedback to apply: {context.feedback}",
                expected_output="A revised version of the email meeting all constraints.",
                agent=copywriting_agent
            )
            crew = Crew(agents=[copywriting_agent], tasks=[revision_task])
            revised_draft = crew.kickoff()
            self.state['current_draft'] = str(revised_draft)
            return self.state['current_draft']
        
        return self.state['current_draft']

    @listen("approved")
    def execute_campaign(self, result: HumanFeedbackResult):
        print(f"Approval received from Account Executive: {result.feedback}")
        print("Executing API call to CRM/Outreach to queue the email send.")

    @listen("rejected")
    def abort_campaign(self, result: HumanFeedbackResult):
        print(f"Draft rejected by Account Executive. Reason: {result.feedback}")
        print("Logging failure to RLHF pipeline to improve future drafting templates.")

if __name__ == "__main__":
    flow = RevenueRecoveryFlow()
    flow.kickoff()
