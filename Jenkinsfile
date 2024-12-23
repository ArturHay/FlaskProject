pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                // Cloner le code depuis GitHub via SSH
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
                    // Utiliser la clé SSH pour transférer le fichier
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
                    // Utiliser la clé SSH pour déployer sur le VPS
                    withCredentials([sshUserPrivateKey(
                        credentialsId: '639d8da5-12d0-439f-ae69-b5f7e615ee0c',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )]) {
                        sh """
                          ssh -o StrictHostKeyChecking=no -i \$SSH_KEY \$SSH_USER@185.158.132.195 << 'EOSSH'
                            # Charger l'image Docker
                            docker load -i /root/flaskapp.tar

                            # Vérifier si le conteneur existe déjà
                            if [ \$(docker ps -a -q -f name=flask_app_container) ]; then
                                echo "Stopping and removing existing container..."
                                docker stop flask_app_container || true
                                docker rm flask_app_container || true
                            fi

                            # Lancer un nouveau conteneur
                            echo "Starting new container..."
                            docker run -d --name flask_app_container -p 8877:8877 flask-app:latest

                            # Supprimer le fichier transféré
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
            // Nettoyage après chaque exécution
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
