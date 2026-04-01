FROM alpine:latest

# Copy our script into the image
COPY app.sh /app.sh

# Make it executable
RUN chmod +x /app.sh

# Default command when the container starts
CMD ["/app.sh"]
