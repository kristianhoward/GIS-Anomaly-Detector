pipeline {
    agent any

    environment {
        TEST_PATH = "tests\\test_data.py"
    }

    stages {
        stage('Clone') {
            steps {
                git branch: 'main',
                    credentialsId: 'github-creds',
                    url: 'https://github.com/kristianhoward/GIS-Anomaly-Detector'
            }
        }

        stage('Setup & Test') {
            steps {
                bat """
                    IF NOT EXIST venv (
                        python -m venv venv
                        call venv\\Scripts\\activate

                        pip install --upgrade pip
                        pip install .
                        pip install -r server\\requirements.txt
                    ) ELSE (
                        call venv\\Scripts\\activate
                    )
                    pytest %TEST_PATH%
                """
            }
        }
    }
}
