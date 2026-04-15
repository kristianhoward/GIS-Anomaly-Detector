pipeline {
    agent any
    environment {
        TEST_PATH = "C:\\Users\\bbkkr\\GitHub\\GIS-Anomaly-Detector\\tests\\test_data.py"
    }
    stages {
        stage('Clone'){
            steps {
                git branch: 'main',
                credentialsId: 'github-creds',
                url: 'https://github.com/kristianhoward/GIS-Anomaly-Detector'
            }
        }
        stage('VenvSetup') {
            steps {
                bat """
                    python3 -m venv venv
                    call venv/bin/activate
                    pip install .
                    pip install -r server/requirements.txt
                """
            }
        }
        stage('RunTests') {
            steps {
                bat """
                    pytest "%TEST_PATH%"
                """
            }
        }
    }
}
