pipeline {
    agent any

    stages {

        stage ('[Step 00] - Test if EVE-NG VM is reachable') {
            steps {
                dir("scripts/vm/") {
                   sh label: '', script: 'chmod 777 ./test_port.sh'
                   sh label: '', script: './test_port.sh'
                }
            }
        }

        stage('[Step 01] - Deploy_Virutal_Network') {
            steps {
                dir ("scripts") {
                    sh label: '', script: 'chmod 777 ./eveng-api.py'
                    sh label: '', script: './eveng-api.py --deploy=./../topology/topology.yml --force=True'
                }
                post {
                always {
                    echo '[Step 00] - Test connexion to EVE-NG ...'
                }
                success {
                    echo '[Step 00] - Connexion to EVE-NG is ok.'
                }
                failure {
                    echo '[Step 00] - Connexion to EVE-NG failed !'
                    telegramSend("[Step 00] - Connexion to EVE-NG failed for <${JOB_NAME} #${BUILD_ID}> !")
                }
            }

            }
            post {
                always {
                    echo '[Step 01] - Network deployment is finished ...'
                }
                success {
                    echo '[Step 01] - Network is correctly deployed'
                }
                failure {
                    echo '[Step 01] - Network deployement failed !'
                    telegramSend("[Step 01] - Network deployment failed for <${JOB_NAME} #${BUILD_ID}> !")
                }
            }
        }

        stage('[Step 02] - Configure_Virutal_Network') {
            steps {
                sleep 30
                sh 'cat ./topology/hosts'
                ansiblePlaybook installation: 'Ansible', inventory: './topology/hosts', playbook: './deploy_fabric.yml'
            }
            post {
                always {
                    echo '[Step 02] - Network configuration is finished ...'
                }
                success {
                    echo '[Step 02] - Network is correctly configured'
                }
                failure {
                    echo '[Step 02] - Network configuration failed !'
                    telegramSend("[Step 02] - Network configuration failed for <${JOB_NAME} #${BUILD_ID}> !")
                }
            }
        }


        stage('[Step 03] - Execute_Network_Tests') {
            steps {
                dir ("tests") {
                    sh label: '', script: 'chmod 777 ./network-tests.py'
                    sh label: '', script: './network-tests.py'
                }
            }
            post {
                always {
                    echo '[Step 03] - Network tests is finished ...'
                }
                success {
                    echo '[Step 03] - Network has been successfully tested'

                }
                failure {
                    echo '[Step 03] - Network tests failed !'
                    telegramSend("[Step 03] - Network tests failed for <${JOB_NAME} #${BUILD_ID}> !")
                }
            }
        }
    }
}
