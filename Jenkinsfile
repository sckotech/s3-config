pipeline {
    agent any
    environment {
       SONAR_HOME= tool "sonar"
       DOCKERHUB_CREDENIALS = "dockerhub-login"
       DOCKER_IMAGE_NAME = "test/nginx:latest"
    }
    stages{
        stage("Git Checkout"){
            steps{
                git url: "https://github.com/test/s3-config.git", branch: "main"
            }
        }
        stage('Secrets Scanning') {
            parallel {
                stage('TruffleHog Scan') {
                    steps   {
                        sh  '''
                         trufflehog  filesystem --no-update . --json > trufflehog-report.json
                            '''
         
                    }
                    post {
                        always      {
                        archiveArtifacts artifacts: 'trufflehog-report.json'
                        }
                    }
                }

                stage('GitLeaks Scan') {
                    steps   {
                     sh 'gitleaks detect --source ./core --exit-code 0'
                
                    }
                }
            }
        }    
        stage("Sonarqube Quality Analysis"){
            steps{
                withSonarQubeEnv("sonar"){
                    sh "$SONAR_HOME/bin/sonar-scanner -Dsonar.projectName=wanderlust -Dsonar.projectKey=wanderlust"
                }
            }
        }
        stage("Sonar Quality Gate Scan"){
            steps{
                timeout(time: 2, unit: "MINUTES"){
                    waitForQualityGate abortPipeline: false
                }
            }
        }
        stage("Trivy File System Scan"){
            steps{
                sh "trivy fs --format table -o trivy-fs-report.html ."
            }
        }
        stage("Build Image") {
            steps {
                sh "docker build -t ${DOCKER_IMAGE_NAME} ."
            }
            
        }
        stage("Trivy Image Scan"){
            steps{
                 sh "trivy image --exit-code 0 --severity CRITICAL,HIGH ${DOCKER_IMAGE_NAME}"
            }
        }
        stage("Dockerhub Push Image") {
            steps {
                     withCredentials([usernamePassword(credentialsId: 'dockerhub-login',
                                      usernameVariable: 'DOCKER_USER',
                                      passwordVariable: 'DOCKER_PWD')]) {
                     sh '''
                        echo "$DOCKER_PWD" | docker login -u "$DOCKER_USER" --password-stdin
                        
                     '''
                      sh "docker push ${DOCKER_IMAGE_NAME}"
                      sh "docker logout"  
                     }
            }
        }
        stage("DAST Scan ") {
             
            steps {
                 // Example: Deploy temporary container
                 sh 'docker run -d -p 81:80 --name temp-dast-test ${DOCKER_IMAGE_NAME}'
                 
                 // Run ZAP Scan against http://localhost:8080 
                 // (Using ZAP Docker or plugin)
                 sh 'docker run -t owasp/zap2docker-weekly zap-full-scan.py -t http://host.docker.internal:81 -r zap_report.html || true' 
                 
                 // Clean up temporary container
                 sh 'docker stop temp-dast-test && docker rm temp-dast-test'
            }
        }
    }
}
