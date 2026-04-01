FROM alpine:latest

# Default values for environment variables
ENV APP_NAME=my-app
ENV APP_ENV=development
ENV APP_PORT=8080

COPY app.sh /app.sh
RUN chmod +x /app.sh

CMD ["/app.sh"]
