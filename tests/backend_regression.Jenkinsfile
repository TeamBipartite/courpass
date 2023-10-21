pipeline{

    agent any

    stages{
        stage('Setup workspace'){
            steps {
                sh script: 'python3 -m pip --no-input install pytest', label: 'install pytest'
                sh script: 'python3 -m pip --no-input install pytest-custom_exit_code', label: 'install pytest plugins'
                sh script: 'python3 -m pip --no-input install selenium', label: 'install Selenium'
                sh script: 'python3 -m pip --no-input install beautifulsoup4', label: 'install BeautifulSoup'
            }
        }
        stage('Pytest tests'){
            steps {
                sh script: 'python3 -m pytest --junitxml=results.xml --suppress-tests-failed-exit-code tests/test_calendar_scrape.py', label: 'run regression'
            }
        }
    }
    post{
        always{
            junit 'results.xml'
        }
    }
}

