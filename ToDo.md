# Research Plan
The goal is to download MCP github repositories and data mine them for vulnerabilites 

- [ ] Write Script to download repos
- [ ] cluster README.mds to get a general overview of what the servers do
- [ ] Simple analysis of repos
        - [ ] Amount of files per repo -> show distribution
        - [ ] Dominant Laguage per REpository
        - [ ] Number of Commits
        - [ ] Number of branches
        - [ ] Overall File Type Count & Percentage
        - [ ] ? Lines of code per Repo ? -> Distribution
        - [ ] ? Most used dependencies -> any vulnerable ?
        - [ ] count of repos with outdated Dpendencies
- [ ] Run openrep against each repo
- [ ] Statistics of opengrep output: e.g Count type per finding
- [ ] run truffelhog against repos to find secrets/keys
- [ ] if docker images maybe run trivy or grype
- [ ] Run GraphQL against all repos ? or only against those with finidngs from opengrep ?
- [ ] Compare opengrep vs graphql findings

- [ ] Look through the findings and search for actual vulnerabilities
    - [ ] Create list of repos to look at
    - [ ] read code to see wether a vulnerability is present
    - [ ] verify findings


# Write results into README.md
- [ ] Introduction: motivation datamine for vulns with opengrep/ graphql, write down steps in as much detail as possible, so people can reproduce
- [ ] What is MCP
- [ ] Get Repos
- [ ] Statistical Analysis of files
- [ ] Static Code Analysis: what is it, which tools are we going to use ( maybe put this into introduction ??? )
    - [ ] Create all iamges of distributions, charts, etc (cytoscape.js ???)
- [ ] Results of opengrep
- [ ] Results of GraphQL
- [ ] Comapre results
- [ ] Selection of repos to take a deeper look at
- [ ] Repo Analysis fo Selection
- [ ] Conclusion