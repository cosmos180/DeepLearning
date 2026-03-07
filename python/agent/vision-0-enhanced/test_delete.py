import asyncio
import uuid
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        # 1. Create a dummy project
        res_start = await client.post('http://localhost:8765/api/project/start', json={
            'seed': 'test delete script',
            'target_duration': '30分钟短片',
            'style': '默认'
        })
        print("Start:", res_start.json())
        project_id = res_start.json().get('project_id')
        
        # 2. Try to get projects
        res_list = await client.get('http://localhost:8765/api/projects')
        print("Projects:", [p['project_id'] for p in res_list.json()['projects']])
        
        # 3. Delete the project
        res_del = await client.delete(f'http://localhost:8765/api/project/{project_id}')
        print("Delete:", res_del.json())
        
        # 4. Verify deletion
        res_list2 = await client.get('http://localhost:8765/api/projects')
        projects2 = [p['project_id'] for p in res_list2.json()['projects']]
        print("Projects after:", projects2)
        if project_id in projects2:
            print("FAILED to delete")
        else:
            print("Successfully deleted")

asyncio.run(main())
