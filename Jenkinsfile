pipeline {
    agent none

    stages {
        stage('ncf') {
            agent {
                dockerfile true
            }
            steps {
                    sh script: 'make test', label: 'test methods'
            }
        }
    }
}
