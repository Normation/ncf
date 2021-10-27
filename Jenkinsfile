pipeline {
    agent none

    stages {
        stage('ncf') {
            agent {
                dockerfile true
            }
            steps {
                    sh script: 'PATH="/opt/rudder/bin:$PATH" make test', label: 'test methods'
            }
        }
    }
}
