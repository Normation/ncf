pipeline {
    agent none

    stages {
        stage('ncf') {
            agent {
                dockerfile true
            }
            steps {
                dir('language') {
                    sh script: 'make test', label: 'test methods'
                }
            }
        }
    }
}
