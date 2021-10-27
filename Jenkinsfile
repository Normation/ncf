pipeline {
    agent none
    triggers { cron('@daily') }
    stages {
        stage('ncf') {
            agent {
                dockerfile
            }
            steps {
                dir('language') {
                    sh script: 'make test', label: 'test methods'
                }
            }
        }
    }
}
