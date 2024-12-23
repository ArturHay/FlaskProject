pipeline {
    agent any

    stages {
        // plus besoin du stage('Checkout'), Jenkins a déjà fait un checkout avant
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
                    withCredentials([sshUserPrivateKey(credentialsId: 'vps-ssh-cred',
                                                       keyFileVariable: 'SSH_KEY',
                                                       usernameVariable: 'SSH_USER')]) {
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
                    withCredentials([sshUserPrivateKey(credentialsId: 'vps-ssh-cred',
                                                       keyFileVariable: 'SSH_KEY',
                                                       usernameVariable: 'SSH_USER')]) {
                        sh """
                          ssh -o StrictHostKeyChecking=no -i \$SSH_KEY \
                              \$SSH_USER@185.158.132.195 << 'EOSSH'
                                docker load -i /root/flaskapp.tar
                                docker stop flask_app_container || true
                                docker rm flask_app_container || true
                                docker run -d --name flask_app_container -p 8877:8877 flask-app:latest
                                rm /root/flaskapp.tar
                          EOSSH
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            // Nettoyage local
            sh 'rm -f flaskapp.tar || true'
        }
        success {
            echo 'Deployment succeeded!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}
