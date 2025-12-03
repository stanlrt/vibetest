import dspy
from pydantic import BaseModel, Field
from typing import List

# 1. Pydantic Models (The Strict Schema)


class UXTask(BaseModel):
    number: int = Field(
        ...,
        description="The sequence number of the task, starting from 1."
    )
    requirement: str = Field(
        ...,
        description="The high-level requirement. MUST specify the Actor (e.g., 'User 1 (Host) must...')."
    )
    steps: List[str] = Field(
        ...,
        description="A list of STRICTLY ATOMIC actions. Must start with verbs like: 'Locate', 'Click', 'Type', 'Verify', 'Wait', 'Scan', 'Switch', or 'Open'."
    )
    acceptance_criteria: str = Field(
        ...,
        description="The specific visible outcome that confirms success."
    )


class TestScriptOutput(BaseModel):
    # 'reasoning' is defined first to enforce Chain-of-Thought behavior within the JSON generation.
    reasoning: str = Field(
        ...,
        description="Step-back analysis: 1. Map Resource Lifecycle (Create -> Join). 2. Identify Negative Tests (errors/disabled states). 3. Plan Tab switching."
    )
    ux_tasks: List[UXTask] = Field(
        ...,
        description="The linear, executable list of UX tasks."
    )

# 2. DSPy Signature (The System Prompt)


class TestScriptSignature(dspy.Signature):
    """
    Translate a conversation log into a linear, executable QA test script for browser automation.

    CRITICAL CONSTRAINTS:
    1. ATOMICITY: Steps must be single actions. Never combine actions (e.g., "Login and Click" is FORBIDDEN).
       - BAD: "Navigate to URL and login"
       - GOOD: "Open new tab", "Navigate to URL", "Type 'user'", "Click 'Login'"
    2. NEGATIVE TESTING: Verify error states or disabled buttons BEFORE performing the successful action.
    3. TAB MANAGEMENT: Explicitly manage state. Use "Switch to tab 1" or "Open new tab for User 2".
    4. LIFECYCLE: A resource must be CREATED (User 1) before it can be JOINED (User 2).
    5. IMPLICIT EDGE CASES: Beyond explicit requirements, infer what SHOULD fail based on common sense:
       - If there's authentication, test accessing protected resources without logging in.
       - If there are inputs with logical constraints, test invalid/impossible values.
       - If there's authorization (roles/ownership), test actions by unauthorized users.
       - If there's data validation, test boundary violations the app should reject.
    """

    conversation_log: str = dspy.InputField(
        desc="The raw conversation log or requirements text.")

    # In DSPy 3.0, dspy.Predict uses this type hint to structure the output automatically.
    output: TestScriptOutput = dspy.OutputField(
        desc="The structured test script.")

# 3. DSPy Module (The Logic)


class QAArchitect(dspy.Module):
    def __init__(self):
        super().__init__()
        # FIX: Replaced 'TypedPredictor' (removed in 3.0) with 'dspy.Predict'.
        # dspy.Predict now handles Pydantic outputs natively.
        self.generate_script = dspy.Predict(TestScriptSignature)

    def forward(self, conversation_log: str) -> dspy.Prediction:
        return self.generate_script(conversation_log=conversation_log)

# 4. Optimization & Execution Setup


if __name__ == "__main__":
    from dspy.teleprompt import BootstrapFewShot

    # --- Configuration ---
    # We use a dummy setup to ensure the script runs immediately for you.
    # To use real AI, uncomment: dspy.configure(lm=dspy.LM("openai/gpt-4o"))

    if dspy.settings.lm is None:
        print("⚠️ No LM configured. Using DummyLM for syntax validation.")

        # Valid dummy response adhering to strict atomicity rules
        dummy_content = TestScriptOutput(
            reasoning="Dummy reasoning: Create (User 1) -> Negative Test -> Join (User 2).",
            ux_tasks=[
                UXTask(
                    number=1,
                    requirement="User 1 creates game",
                    steps=["Open new tab", "Navigate to URL", "Click 'Create'"],
                    acceptance_criteria="Game Created"
                )
            ]
        ).model_dump_json()

        # Use DummyLM to simulate a model response without an API key
        model = dspy.DummyLM([dummy_content])  # type: ignore[attr-defined]
        dspy.settings.configure(lm=model)
    else:
        print(f"✅ Using configured LM: {dspy.settings.lm}")

    # --- Training Data (Gold Standard Examples) ---

    example1_input = """User: "I need a login form. Button disabled if password short. Remove 'Forgot Password'." """
    example1_output = TestScriptOutput(
        reasoning="Identified 'Login' flow. Negative constraint (disabled button) must be tested BEFORE positive action.",
        ux_tasks=[
            UXTask(number=1, requirement="Verify 'Login' button is disabled (Negative Test)",
                   steps=["Locate 'Password' input", "Type '123'",
                          "Locate 'Login' button", "Verify element is disabled"],
                   acceptance_criteria="Button disabled"),
            UXTask(number=2, requirement="User logs in successfully",
                   steps=["Locate 'Password' input",
                          "Type 'validPass'", "Click 'Login' button"],
                   acceptance_criteria="Dashboard visible")
        ]
    )

    example2_input = """User: "Host creates room first. User can't join if room doesn't exist." """
    example2_output = TestScriptOutput(
        reasoning="User 1 (Host) must Create Room (Task 2) before User 2 can Join. Added negative test first.",
        ux_tasks=[
            UXTask(number=1, requirement="Verify User 2 cannot join non-existent room",
                   steps=["Open new tab", "Navigate to URL", "Type '9999'",
                          "Click 'Join'", "Verify error message"],
                   acceptance_criteria="Error displayed"),
            UXTask(number=2, requirement="User 1 (Host) creates room",
                   steps=["Switch to tab 1",
                          "Click 'Create Room'", "Verify Code"],
                   acceptance_criteria="Code displayed")
        ]
    )
    example_negative = """User: "Ensure users can't login with bad passwords." """
    example_negative_output = TestScriptOutput(
        reasoning="Security check first. Negative test (Invalid Login) -> Positive test (Valid Login).",
        ux_tasks=[
            UXTask(number=1, requirement="Verify login fails with invalid password",
                   steps=["Type 'wrongpass'", "Click 'Login'",
                          "Verify error message"],
                   acceptance_criteria="Error displayed"),
            UXTask(number=2, requirement="User logs in successfully",
                   steps=["Type 'correctpass'", "Click 'Login'"],
                   acceptance_criteria="Dashboard visible")
        ]
    )

    # Implicit edge case example: authentication/authorization
    example_implicit_edge = """User: "Users can view their own profile and edit their bio." """
    example_implicit_edge_output = TestScriptOutput(
        reasoning="Implicit edge cases: 1. Unauthenticated access to profile page should fail. 2. User should not edit another user's profile. Test these BEFORE the happy path.",
        ux_tasks=[
            UXTask(number=1, requirement="Verify unauthenticated user cannot access profile page",
                   steps=["Open new tab", "Navigate to '/profile'",
                          "Verify redirect to login or error message"],
                   acceptance_criteria="User is redirected to login or sees 'Please log in' message"),
            UXTask(number=2, requirement="Verify user cannot edit another user's profile",
                   steps=["Navigate to '/profile/other-user-id'",
                          "Locate 'Edit Bio' button", "Verify element is disabled or not visible"],
                   acceptance_criteria="Edit functionality is not available for other users' profiles"),
            UXTask(number=3, requirement="User edits their own bio successfully",
                   steps=["Navigate to '/profile'", "Click 'Edit Bio'",
                          "Type 'New bio text'", "Click 'Save'"],
                   acceptance_criteria="Bio updated successfully")
        ]
    )

    # Implicit edge case example: logical/data validation constraints
    example_logical_constraint = """User: "Users can set a price range filter with min and max values." """
    example_logical_constraint_output = TestScriptOutput(
        reasoning="Implicit edge cases: 1. Min > Max is logically impossible, should be rejected. 2. Negative prices may be invalid. Test invalid inputs BEFORE valid filter.",
        ux_tasks=[
            UXTask(number=1, requirement="Verify app rejects impossible range (min greater than max)",
                   steps=["Locate 'Min Price' input", "Type '500'",
                          "Locate 'Max Price' input", "Type '100'",
                          "Click 'Apply Filter' button", "Verify error message"],
                   acceptance_criteria="Error displayed indicating min must be less than max"),
            UXTask(number=2, requirement="Verify app rejects negative price values",
                   steps=["Locate 'Min Price' input", "Type '-50'",
                          "Click 'Apply Filter' button", "Verify error message"],
                   acceptance_criteria="Error displayed indicating price cannot be negative"),
            UXTask(number=3, requirement="User applies valid price range filter",
                   steps=["Locate 'Min Price' input", "Type '100'",
                          "Locate 'Max Price' input", "Type '500'",
                          "Click 'Apply Filter' button", "Verify results filtered"],
                   acceptance_criteria="Results show only items within price range")
        ]
    )

    trainset = [
        dspy.Example(conversation_log=example1_input,
                     output=example1_output).with_inputs("conversation_log"),
        dspy.Example(conversation_log=example2_input,
                     output=example2_output).with_inputs("conversation_log"),
        dspy.Example(conversation_log=example_negative,
                     output=example_negative_output).with_inputs("conversation_log"),
        dspy.Example(conversation_log=example_implicit_edge,
                     output=example_implicit_edge_output).with_inputs("conversation_log"),
        dspy.Example(conversation_log=example_logical_constraint,
                     output=example_logical_constraint_output).with_inputs("conversation_log"),
    ]

    # --- Metric Function (The Quality Gate) ---
    def validate_script_quality(example, pred, trace=None):
        """
        Checks for: Valid JSON, Non-empty lists, and Strict Atomicity.
        """
        try:
            # 1. Structural Integrity
            if not hasattr(pred, "output") or pred.output is None:
                return False
            if not isinstance(pred.output, TestScriptOutput):
                return False
            if not pred.output.ux_tasks:
                return False

            # 2. Logic & Atomicity Checks
            ALLOWED_VERBS = ["Locate", "Click", "Type",
                             "Verify", "Wait", "Scan", "Switch", "Open"]

            for task in pred.output.ux_tasks:
                if not task.steps:
                    return False  # Empty steps
                if not task.requirement.strip():
                    return False  # Empty requirement

                # Check each step for atomicity
                for step in task.steps:
                    # Step must start with an allowed verb
                    first_word = str(step).strip().split(' ')[0]
                    if first_word not in ALLOWED_VERBS:
                        return False

            return True

        except Exception:
            return False

    # --- Compilation ---
    print("Compiling QAArchitect...")

    teleprompter = BootstrapFewShot(
        metric=validate_script_quality,
        max_bootstrapped_demos=2
    )

    try:
        compiled_architect = teleprompter.compile(
            QAArchitect(), trainset=trainset)
        print("✅ Compilation successful!")

        # Save the optimized prompt logic
        compiled_architect.save("qa_architect_compiled.json")

        # Test Run
        test_input = "User: I want to be able to edit my profile. But first I need to register."
        print(f"\nRunning test on: '{test_input}'")

        pred = compiled_architect(conversation_log=test_input)

        print("\nPrediction Result:")
        print(pred.output.model_dump_json(indent=2))

    except Exception as e:
        print(f"\n❌ Execution failed: {e}")
        print("Ensure you have a valid LM configured if you aren't using DummyLM.")
