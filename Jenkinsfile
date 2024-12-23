pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                // Cloner le code source depuis GitHub
                checkout([$class: 'GitSCM',
                          branches: [[name: '*/main']],
                          userRemoteConfigs: [[
                              url: 'git@github.com:ArturHay/FlaskProject.git',
                              credentialsId: 'jenkins'
                          ]]
                ])
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Construire l'image Docker (tag = flask-app:latest)
                    sh 'docker build -t flask-app:latest .'
                }
            }
        }

        stage('Save Docker Image') {
            steps {
                script {
                    // Exporter l'image dans un fichier tar (flaskapp.tar)
                    sh 'docker save flask-app:latest -o flaskapp.tar'
                }
            }
        }

        stage('Transfer to VPS') {
            steps {
                script {
                    // Transférer flaskapp.tar sur le VPS via scp
                    // On récupère la clé SSH du VPS via un Credential Jenkins (vps-ssh-cred)
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
                    // Se connecter au VPS, charger l'image et lancer le conteneur
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
            // Nettoyage : supprimer le fichier tar local (runner Jenkins)
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
