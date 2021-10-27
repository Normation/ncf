pipeline {
    agent none

    stages {
        stage('ncf') {
            agent {
                dockerfile true
            }
            environment {
                PATH = "/opt/rudder/bin:${env.PATH}"
            }
            steps {
                    sh script: 'make test', label: 'test methods'
            }
        }
    }
}
