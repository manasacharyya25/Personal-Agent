Check the workspace. Its a scattered pieces of python files that I worked on to learn fast api and a rag pipeline

I now wish to build the actual thing. 

It will work across several platforms.  
  
Here are some of the usecases for the agent.  
  
-- REDDIT --  
1. Check reddit for users of RhoQ and talk to them about RhoQ  
2. Check reddit for job posting ( hiring and apply automatically using new email id )  
3. Check for small business and anyone who might be interested in an AI Agentic workflow ( businesses as clients ) and get in touch

-- UPWORK AND LINKEDIN --  
4. Look for jobs and apply  
5. Look for interesting post on linkedin that could be reposted on twitter

-- INSTAGRAM --  
6. Look for interesting posts that can be posted to twitter  
7. Look for Users who might be interested in using RHoQ,  
8. Approach Fitness creators / Comment on their posts  
9. Create a profile following on Instagram

-- X --  
10. Reply to posts and comments  
11. Post on a schedule what has been collected from LinkedIn and Instagram  
12. Also check for posts self created but scheduled  
13. Run an analysis on self posts to see what gets highest engagement, what time etc  
14. Always search for new people to connect with

-- SLACK --  
15. Read any post and message and inform me on WhatsApp if anything is important  
  
-- Vercel --  
16. Check analytics for my projects and tell me what changed  
17. Check supabase dbs and tell me when something new happens in the platforms ( new user signups, new plan generation, new posts, new lives )  
  
The product architecture has followign modules   
                ┌──────────────────┐
                │ Extraction Bots  │
                │                  │
                │ Reddit           │
                │ LinkedIn         │
                │ Instagram       │
                │ X / Slack        │
                │ Supabase/Vercel  │
                └────────┬─────────┘
                         ↓
                       DB
                         ↓
                ┌──────────────────┐
                │  Matcher Bots    │
                │                  │
                │ Job ↔ Skills     │
                │ Lead ↔ RhoQ      │
                │ Content scoring  │
                └────────┬─────────┘
                         ↓
                    Notification
                         ↓
                       YOU
                         ↓
                ┌──────────────────┐
                │      AGENT       │
                │                  │
                │ Reason           │
                │ Generate         │
                │ Decide           │
                │ Converse         │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │  Browser/Action  │
                │      Bots        │
                │                  │
                │ Playwright       │
                │ APIs             │
                └──────────────────┘  
  
The codebase structure should be something like this   
  
agent/
│
├── apps/
│   │
│   ├── agent/
│   │   ├── [main.py](http://main.py)
│   │   ├── agent_[service.py](http://service.py)
│   │   ├── [tools.py](http://tools.py)
│   │   └── prompts/
│   │       ├── [system.md](http://system.md)
│   │       └── [proposal.md](http://proposal.md)
│   │
│   ├── extraction/
│   │   ├── [main.py](http://main.py)
│   │   ├── [reddit.py](http://reddit.py)
│   │   ├── [linkedin.py](http://linkedin.py)
│   │   ├── [instagram.py](http://instagram.py)
│   │   └── [twitter.py](http://twitter.py)
│   │
│   ├── evaluator/
│   │   ├── [main.py](http://main.py)
│   │   ├── job_[matcher.py](http://matcher.py)
│   │   ├── lead_[matcher.py](http://matcher.py)
│   │   └── prompts/
│   │       ├── job_[evaluation.md](http://evaluation.md)
│   │       └── lead_[evaluation.md](http://evaluation.md)
│   │
│   └── actor/
│       ├── [main.py](http://main.py)
│       ├── [reddit.py](http://reddit.py)
│       ├── [instagram.py](http://instagram.py)
│       ├── [twitter.py](http://twitter.py)
│       └── playwright/
│           ├── [upwork.py](http://upwork.py)
│           └── [linkedin.py](http://linkedin.py)
│
├── packages/
│   │
│   ├── database/
│   │   ├── [database.py](http://database.py)
│   │   ├── [models.py](http://models.py)
│   │   └── repositories/
│   │
│   ├── llm/
│   │   ├── [client.py](http://client.py)
│   │   ├── [embeddings.py](http://embeddings.py)
│   │   └── [reasoning.py](http://reasoning.py)
│   │
│   ├── prompts/
│   │   └── shared/
│   │       ├── [classify.md](http://classify.md)
│   │       └── [summarize.md](http://summarize.md)
│   │
│   ├── queue/
│   │   ├── [queue.py](http://queue.py)
│   │   └── [jobs.py](http://jobs.py)
│   │
│   ├── common/
│   │   ├── [config.py](http://config.py)
│   │   ├── [logger.py](http://logger.py)
│   │   └── [schemas.py](http://schemas.py)
│   │
│   └── integrations/
│       ├── [whatsapp.py](http://whatsapp.py)
│       ├── [reddit.py](http://reddit.py)
│       ├── [linkedin.py](http://linkedin.py)
│       ├── [instagram.py](http://instagram.py)
│       └── [twitter.py](http://twitter.py)
│
├── knowledge/
│   ├── rhoq/
│   │   └── [knowledgebase.md](http://knowledgebase.md)
│   ├── thoughtspace/
│   │   └── [knowledgebase.md](http://knowledgebase.md)
│   └── personal/
│       └── [skills.md](http://skills.md)
│
├── ingestion/
│   ├── [scripts.py](http://scripts.py)
│   └── chunk_embed_[save.py](http://save.py)
│
├── dashboard/
│   ├── frontend/
│   │   └── ...
│   └── api/
│       └── ...
│
├── migrations/
│
├── tests/
│
├── .env
├── pyproject.toml
└── [README.md](http://README.md)  
  
  
