pipeline{

    agent any

    stages{
        stage('Setup workspace'){
            steps {
                sh script: 'python3 -m pip --no-input install pytest'
            }
        }
        stage('Pytest tests'){
            steps {
                sh script: 'python3 -m pytest --junitxml=results.xml tests/test_calendar_scrape.py', label: 'run regression'
            }
        }
    }
}    
