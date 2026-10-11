from agent import agent


query = "What is the address of TechSimPlus Learnings"
res = agent.invoke(
    {"messages": [ {"role":"user", "content":query} ]}
)

answer = res["messages"][-1].content
print(answer)