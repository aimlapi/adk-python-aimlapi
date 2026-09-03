# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import asyncio
import os
import time

import agent
from dotenv import load_dotenv
from google.adk import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.cli.utils import logs
from google.adk.sessions import InMemorySessionService
from google.adk.sessions import Session
from google.genai import types

load_dotenv(override=True)
logs.log_to_tmp_folder()


async def main():
  # Check for the aimlapi.com API key. LiteLLM reads AIML_API_KEY.
  if not os.environ.get('AIML_API_KEY'):
    print(
        ' Your AIML_API_KEY is not set. Set it before you continue by'
        ' running the following code:'
    )
    print(" export AIML_API_KEY='your-aimlapi-key'")
    return

  app_name = 'aimlapi_app'
  user_id_1 = 'user1'
  session_service = InMemorySessionService()
  artifact_service = InMemoryArtifactService()
  runner = Runner(
      app_name=app_name,
      agent=agent.root_agent,
      artifact_service=artifact_service,
      session_service=session_service,
  )
  session_11 = await session_service.create_session(
      app_name=app_name, user_id=user_id_1
  )

  async def run_prompt(session: Session, new_message: str):
    content = types.Content(
        role='user', parts=[types.Part.from_text(text=new_message)]
    )
    print('** User says:', content.model_dump(exclude_none=True))
    async for event in runner.run_async(
        user_id=user_id_1,
        session_id=session.id,
        new_message=content,
    ):
      if event.content.parts and event.content.parts[0].text:
        print(f'** {event.author}: {event.content.parts[0].text}')

  start_time = time.time()
  print('Start time:', start_time)
  print('------------------------------------')
  print('Testing aimlapi.com integration with ADK')
  print('Model: aiml/openai/gpt-4o-mini')
  print('------------------------------------')
  await run_prompt(session_11, 'Hi, introduce yourself.')
  # A second turn on the same session is the one that matters: it replays the
  # tool call and its result back to the model.
  await run_prompt(
      session_11,
      'Roll a die with 20 sides and check if the result is prime.',
  )
  end_time = time.time()
  print('------------------------------------')
  print('End time:', end_time)
  print('Total time:', end_time - start_time)


if __name__ == '__main__':
  asyncio.run(main())
