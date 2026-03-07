import asyncio
from backend.core.blackboard import blackboard

async def main():
    await blackboard.init()
    projects = await blackboard.get_all_projects()
    if not projects:
        print("No projects found.")
        return
    
    # Get the latest project that failed
    failed_projects = [p for p in projects if p['status'] == 'failed']
    if not failed_projects:
        print("No failed projects.")
        # Just print logs for the first project
        p = projects[0]
    else:
        p = failed_projects[0]
        
    print(f"Project ID: {p['project_id']}, Status: {p['status']}")
    
    logs = await blackboard.get_agent_logs(p['project_id'])
    for log in logs:
        print(f"[{log['time']}] {log['agent']} ({log['status']}): {log['message']}")
        if log['detail']:
            print(f"  Detail: {log['detail']}")

asyncio.run(main())
