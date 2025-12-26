# Physical AI Book - Chatbot User Guide

Welcome to the Physical AI & Humanoid Robotics textbook chatbot! This guide will help you make the most of the AI-powered Q&A system.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Asking Questions](#asking-questions)
3. [Using Text Selection](#using-text-selection)
4. [Chapter Filtering](#chapter-filtering)
5. [Understanding Citations](#understanding-citations)
6. [Personalization Features](#personalization-features)
7. [Troubleshooting](#troubleshooting)

## Getting Started

The chatbot is designed to answer questions about the Physical AI & Humanoid Robotics textbook content. Simply type your question in the chat interface and receive responses with citations to the relevant textbook sections.

### What You Can Ask

- Concept explanations: "What is embodied intelligence?"
- Technical details: "How do ROS 2 nodes communicate?"
- Chapter-specific questions: "What are the key principles in Chapter 3?"
- Comparative questions: "How does this differ from traditional robotics?"

### What You Cannot Ask

The chatbot is limited to textbook content only. It cannot:
- Answer questions outside the textbook scope
- Provide real-time information
- Access external resources
- Generate creative content unrelated to the textbook

## Asking Questions

### Best Practices for Questions

1. **Be Specific**: "Explain the control architecture for humanoid robots" is better than "Tell me about robots"

2. **Use Textbook Terminology**: When possible, use the same terms as the textbook for better results

3. **Include Context**: "According to Chapter 5, how does sensor fusion work?" helps narrow the search

4. **Ask One Thing at a Time**: Focused questions typically yield better answers than complex multi-part questions

### Question Examples

**Good Questions:**
- "What is the difference between feedforward and feedback control in robotics?"
- "Explain how inverse kinematics works in Chapter 4"
- "What are the main challenges in humanoid locomotion?"

**Less Effective Questions:**
- "Tell me everything about robotics" (too broad)
- "What's the weather like?" (outside textbook scope)
- "Can you write a poem about AI?" (outside textbook scope)

## Using Text Selection

The chatbot supports contextual questions based on selected text:

1. **Select Text**: Highlight any text in the textbook content
2. **Ask Contextual Questions**: Type your question in the chat
3. **Get Context-Aware Responses**: The chatbot will consider both the selected text and your question

### Examples of Text Selection Use

- Select a paragraph about sensors, then ask "How does this relate to the navigation system?"
- Highlight a code snippet, then ask "Can you explain this algorithm?"
- Select a section about control theory, then ask "What are the practical applications?"

## Chapter Filtering

You can restrict answers to specific chapters:

1. **Use the Chapter Filter**: Select a chapter from the dropdown menu
2. **Ask Your Question**: The response will only use information from the selected chapter
3. **Clear Filter**: Remove the filter to search all chapters again

### When to Use Chapter Filtering

- When studying a specific chapter and want focused information
- When you want to verify understanding of particular concepts
- When comparing how different chapters approach similar topics

## Understanding Citations

### Source Attribution

Every response includes citations showing where the information came from in the textbook:

- **Chapter**: The textbook chapter where the information appears
- **Section**: The specific section within the chapter
- **Score**: Relevance score (higher = more relevant to your question)

### Citation Format

```
[Chapter 1: Introduction to Physical AI]
[Chapter 2: Embodied Intelligence - Section 2.3]
[Chapter 3: Sensor Systems - Section 3.1]
```

### Interpreting Scores

- **0.8+**: Very high relevance
- **0.6-0.8**: High relevance
- **0.4-0.6**: Moderate relevance
- **0.2-0.4**: Low relevance
- **Below 0.2**: May not be directly relevant

## Personalization Features

### User Profiles

When logged in, the chatbot adapts to your technical background:

1. **Technical Level**: Beginner, Intermediate, or Advanced
2. **Programming Experience**: Python, C++, ROS, etc.
3. **Robotics Background**: Academic, Professional, Hobbyist
4. **Learning Goals**: Specific areas of interest

### How Personalization Works

- **Beginner**: Explanations include more foundational concepts and examples
- **Advanced**: Responses may include more technical depth and advanced applications
- **Programming Focus**: More code examples and implementation details
- **Theory Focus**: More conceptual and mathematical explanations

## Troubleshooting

### Common Issues

#### "No Relevant Results Found"
- Try rephrasing your question using different terminology
- Check if your question is within the textbook scope
- Remove chapter filters to search all content
- Use more specific or broader search terms

#### "Question is Outside Textbook Scope"
- The chatbot is limited to textbook content only
- Questions about current events, external resources, or unrelated topics will not be answered
- Try reframing your question to relate to textbook concepts

#### Slow Response Times
- The system may be experiencing high usage
- Check your internet connection
- Try asking a simpler question
- Responses may take longer for complex questions requiring multiple sources

#### Generic or Unhelpful Responses
- Be more specific in your question
- Include context about which chapter or topic you're studying
- Try breaking complex questions into smaller parts

### Tips for Better Results

1. **Be Patient**: Complex questions may take longer to process
2. **Try Different Wording**: Same question, different words may yield better results
3. **Use Chapter Context**: Mention specific chapters when relevant
4. **Combine Features**: Use text selection with chapter filtering for very specific queries

## Rate Limits

The system has rate limits to ensure fair usage:
- **10 requests per minute** per user/session
- If you hit the limit, wait about 1 minute before trying again
- Rate limits reset automatically

## Getting Help

### Within the Chatbot
- Ask "How do I use this chatbot?" for quick help
- Ask "What can you help me with?" for capabilities overview
- Ask "Show me examples" for question examples

### Additional Resources
- Check the textbook for comprehensive coverage of topics
- Use the search function in the textbook for quick lookups
- Refer to the technical documentation if you're implementing systems

## Privacy Notice

- Your questions are stored to improve the system
- Personal information is not required to use basic features
- Login is optional but enables personalization
- Data is used only to improve educational outcomes