import json
import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="Prompt Optimizer",
    page_icon="✨",
    layout="wide"
)

st.title("✨ Prompt Optimizer")

st.write(
    "Improve prompts by increasing clarity, reducing ambiguity, strengthening instructions, and optimizing output quality."
)

api_key = st.secrets.get("OPENAI_API_KEY", None)

if not api_key:
    st.error("OPENAI_API_KEY not found.")
    st.stop()

client = OpenAI(api_key=api_key)

prompt_input = st.text_area(
    "Original Prompt",
    height=250
)

if st.button("✨ Optimize Prompt"):

    if not prompt_input.strip():
        st.warning("Please enter a prompt.")
        st.stop()

    optimization_prompt = f"""
You are an expert Prompt Engineer.

Rewrite the following prompt into a clearer, more robust version while preserving the original intent.

Return ONLY valid JSON.

Schema:

{{
"before_score": 0,
"after_score": 0,
"summary": "",
"improvements": [],
"optimized_prompt": ""
}}

Prompt:

{prompt_input}
"""

    with st.spinner("Optimizing prompt..."):

        response = client.chat.completions.create(
            model="gpt-5-mini",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Prompt Engineer. Always return valid JSON."
                },
                {
                    "role": "user",
                    "content": optimization_prompt
                }
            ]
        )

    try:

        result = json.loads(response.choices[0].message.content)

        st.success("Prompt optimized!")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Before",
                f"{result['before_score']}/100"
            )

        with col2:
            st.metric(
                "After",
                f"{result['after_score']}/100"
            )

        st.info(result["summary"])

        with st.expander("📈 Improvements", expanded=True):

            for item in result["improvements"]:
                st.markdown(f"- {item}")

        st.subheader("Original Prompt")

        st.code(prompt_input)

        st.subheader("Optimized Prompt")

        st.code(result["optimized_prompt"])

        report = f"""# Prompt Optimizer Report

## Before Score

{result['before_score']}/100

## After Score

{result['after_score']}/100

## Summary

{result['summary']}

## Improvements

"""

        for item in result["improvements"]:
            report += f"- {item}\n"

        report += f"""

## Original Prompt

{prompt_input}

## Optimized Prompt

{result['optimized_prompt']}
"""

        st.download_button(
            "📄 Download Markdown Report",
            report,
            file_name="prompt_optimizer_report.md",
            mime="text/markdown"
        )

    except Exception:

        st.error("Model did not return valid JSON.")

        st.code(response.choices[0].message.content)
