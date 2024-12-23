pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout([$class: 'GitSCM',
                          branches: [[name: '*/main']],
                          userRemoteConfigs: [[
                              url: 'git@github.com:ArturHay/FlaskProject.git',
                              credentialsId: '639d8da5-12d0-439f-ae69-b5f7e615ee0c'
                          ]]
                ])
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t flask-app:latest .'
                }
            }
        }

        stage('Save Docker Image') {
            steps {
                script {
                    sh 'docker save flask-app:latest -o flaskapp.tar'
                }
            }
        }

        stage('Transfer to VPS') {
            steps {
                script {
                    withCredentials([sshUserPrivateKey(
                        credentialsId: '639d8da5-12d0-439f-ae69-b5f7e615ee0c',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )]) {
                        sh """
                          scp -o StrictHostKeyChecking=no -i \$SSH_KEY \
                              flaskapp.tar \
                              \$SSH_USER@185.158.132.195:/root/
                        """
                    }
                }
            }
        }

        stage('Deploy on VPS') {
            steps {
                script {
                    withCredentials([sshUserPrivateKey(
                        credentialsId: '639d8da5-12d0-439f-ae69-b5f7e615ee0c',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )]) {
                        // Écrire un script temporaire à exécuter sur le VPS
                        writeFile file: 'deploy.sh', text: '''
                            #!/bin/bash
                            docker load -i /root/flaskapp.tar
                            if [ $(docker ps -a -q -f name=flask_app_container) ]; then
                                echo "Stopping and removing existing container..."
                                docker stop flask_app_container || true
                                docker rm flask_app_container || true
                            fi
                            echo "Starting new container..."
                            docker run -d --name flask_app_container -p 8877:8877 flask-app:latest
                        '''

                        // Transférer et exécuter le script sur le VPS
                        sh """
                          scp -o StrictHostKeyChecking=no -i \$SSH_KEY deploy.sh \$SSH_USER@185.158.132.195:/root/
                          ssh -o StrictHostKeyChecking=no -i \$SSH_KEY \$SSH_USER@185.158.132.195 'bash /root/deploy.sh && rm /root/deploy.sh'
                        """
                    }
                }
            }
        }
    }

    post {
        success {
            echo 'Deployment succeeded!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}
