# Data Generation

For the first step, we generate envProfile (including scenario / social goal / relationship restriction) based on inspiring prompt.

For the second step, we put the original agentProfile and relationshipProfile into our new redis database

For the third step, we combine them together to be combos based on conditiona sampling (the restriction is the relationship)

All the EnvProfile (new generated), AgentProfile (sotopia original), RelationshipProfile (sotopia original), and envagentcombo are on the redis database that is new created.