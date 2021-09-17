@Library('slack-notification')
import org.gradiant.jenkins.slack.SlackNotifier
@Library('rudder-ci-libs@fda') _

pipeline {
    agent none

    stages {
        stage('qa-test') {
            agent { label 'script' }
            environment {
              PATH = "${env.HOME}/.local/bin:${env.PATH}"
            }
            steps {
                sh script: './qa-test', label: 'qa-test'
                sh script: './qa-test --typos', label: 'check typos'
                sh script: './qa-test --quick', label: 'check typos'
            }
        }
        stage('ncf-tests') {
            agent { label 'rtf' }
            steps {
                script {
                    String ncf_path = "${workspace}/ncf"
                    testLocalNcf("ci/rudder-6.1-nightly", ["debian9"], "ncf_path")
                }
            }
        }
    }

    post {
        always {
            script {
                new SlackNotifier().notifyResult("shell-team")
            }
        }
    }
}
