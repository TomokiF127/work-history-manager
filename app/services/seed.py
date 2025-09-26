from models import (
    OS, Language, Framework, Tool, Cloud, DB, Role, Task
)

def seed_initial_data(session):
    try:
        existing_count = session.query(Language).count()
        if existing_count > 0:
            print("初期データは既に投入済みです")
            return
    except Exception:
        pass
    
    os_data = [
        ("Windows 10", None),
        ("Windows 7", None),
        ("CentOS", None),
        ("macOS", None),
        ("Linux", None),
        ("Ubuntu", None),
        ("Red Hat", None),
        ("Windows Server", None),
    ]
    
    language_data = [
        ("Access VBA", "Microsoft Access VBA"),
        ("C", None),
        ("C#", None),
        ("CSS", None),
        ("HTML", None),
        ("Java", None),
        ("JavaScript", None),
        ("JSP", "JavaServer Pages"),
        ("PowerScript", "PowerBuilder script"),
        ("Python", None),
        ("R", None),
        ("React", "React.js"),
        ("TypeScript", None),
        ("Node.js", "JavaScript runtime"),
        ("PHP", None),
        ("Ruby", None),
        ("Go", None),
        ("Swift", None),
    ]
    
    db_data = [
        ("Access", "Microsoft Access"),
        ("DB2", "IBM DB2"),
        ("PostgreSQL", None),
        ("SQL Server", "Microsoft SQL Server"),
        ("Oracle", "Oracle Database"),
        ("MySQL", None),
        ("MongoDB", None),
        ("SQLite", None),
        ("Redis", None),
    ]
    
    framework_data = [
        ("ASP.NET Core", "Microsoft web framework"),
        ("JPA", "Java Persistence API"),
        ("Bootstrap 3", "CSS framework v3"),
        ("jQuery", "JavaScript library"),
        ("JUnit", "Java testing framework"),
        ("MyBatis", "Persistence framework"),
        ("Seasar2", "Java framework"),
        ("Spring", "Java framework"),
        ("Spring Boot", "Spring framework"),
        ("Swagger UI", "API documentation"),
        ("Thymeleaf", "Java template engine"),
        ("Wijmo", "GrapeCity UI components"),
        ("FastAPI", "Python web framework"),
        ("Django", "Python web framework"),
        ("Next.js", "React framework"),
        ("Vue.js", None),
        ("Angular", None),
        ("Express.js", "Node.js framework"),
        ("Flask", "Python micro framework"),
    ]
    
    tool_data = [
        ("A5:SQL Mk-2", "SQL client tool"),
        ("Chatwork", "Business chat tool"),
        ("Docker Desktop", "Container platform"),
        ("Eclipse", "IDE"),
        ("FFFTP", "FTP client"),
        ("Git", "Version control"),
        ("GitHub", "Git hosting service"),
        ("GitLab", "DevOps platform"),
        ("IntelliJ IDEA", "JetBrains IDE"),
        ("Jira", "Issue tracking"),
        ("PowerBuilder", "SAP development tool"),
        ("PyCharm", "Python IDE"),
        ("Redmine", "Project management"),
        ("RStudio", "R IDE"),
        ("Slack", "Team communication"),
        ("Sourcetree", "Git GUI"),
        ("Spring Tool Suite", "Eclipse-based IDE"),
        ("SQL Server Management Studio", "SSMS"),
        ("Teams", "Microsoft Teams"),
        ("TortoiseGit", "Git client"),
        ("Visual Studio", "Microsoft IDE"),
        ("Visual Studio Code", "VS Code"),
        ("Word", "Microsoft Word"),
        ("Zoom", "Video conference"),
        ("サクラエディタ", "Sakura Editor"),
        ("Postman", "API testing"),
        ("Jenkins", "CI/CD"),
        ("Terraform", "IaC tool"),
        ("Kubernetes", "Container orchestration"),
    ]
    
    cloud_data = [
        ("AWS", "Amazon Web Services"),
        ("GCP", "Google Cloud Platform"),
        ("Azure", "Microsoft Azure"),
        ("Heroku", None),
        ("Vercel", None),
        ("Netlify", None),
    ]
    
    role_data = [
        ("リーダー", "Team Leader"),
        ("SE", "System Engineer"),
        ("PG", "Programmer"),
        ("テスター", "Tester"),
        ("PM", "Project Manager"),
        ("アーキテクト", "Architect"),
        ("デザイナー", "Designer"),
        ("サポート", "Support"),
    ]
    
    task_data = [
        ("基本設計", "Basic Design"),
        ("詳細設計", "Detail Design"),
        ("保守", "Maintenance"),
        ("開発", "Development"),
        ("テスト", "Testing"),
        ("要件定義", "Requirement Definition"),
        ("運用", "Operation"),
        ("調査", "Investigation"),
        ("レビュー", "Review"),
        ("リリース", "Release"),
    ]
    
    for name, note in os_data:
        os = OS(name=name, note=note)
        session.add(os)
    
    for name, note in language_data:
        lang = Language(name=name, note=note)
        session.add(lang)
    
    for name, note in db_data:
        db = DB(name=name, note=note)
        session.add(db)
    
    for name, note in framework_data:
        fw = Framework(name=name, note=note)
        session.add(fw)
    
    for name, note in tool_data:
        tool = Tool(name=name, note=note)
        session.add(tool)
    
    for name, note in cloud_data:
        cloud = Cloud(name=name, note=note)
        session.add(cloud)
    
    for name, note in role_data:
        role = Role(name=name, note=note)
        session.add(role)
    
    for name, note in task_data:
        task = Task(name=name, note=note)
        session.add(task)
    
    session.commit()
    print("初期データを投入しました")