run:
	uv sync
	@echo "🚀 Starting OpenCosts Application..."
	@echo "🔍 Checking if Docker is running..."
	@if ! docker info > /dev/null 2>&1; then \
			echo "⚠️ Docker is not running. Attempting to start Docker..."; \
			open -a Docker; \
			for i in $$(seq 1 30); do \
				if docker info > /dev/null 2>&1; then \
					echo "✅ Docker is now running!"; \
					break; \
				fi; \
				echo "⏳ Waiting for Docker to start... ($$i/30)"; \
				sleep 1; \
			done; \
			if ! docker info > /dev/null 2>&1; then \
				echo "❌ Docker is not running and could not be started. Please start Docker manually and try again."; \
				exit 1; \
			fi \
		fi
	@if ! docker info > /dev/null 2>&1; then \
		echo "❌ Docker is not running and could not be started. Please start Docker manually and try again."; \
		exit 1; \
	fi
	@cd docker && \
	echo "📊 Step 1: Running data scraper to generate fresh data..." && \
	docker compose run --rm scraper && \
	echo "✅ Data generation complete!" && \
	echo "🔧 Step 2: Building and starting backend service..." && \
	docker compose up -d backend --build && \
	echo "🎨 Step 3: Building and starting frontend service..." && \
	docker compose up -d frontend --build && \
	for i in $$(seq 1 30); do \
		if curl -s http://localhost:5173 > /dev/null; then \
			echo "✅ Frontend is now running!"; \
			break; \
		fi; \
		echo "⏳ Waiting for frontend to start... ($$i/30)"; \
		sleep 1; \
	done; \
	open http://localhost:5173
	@echo "🌐 Application is now running!"
	@echo "   Backend API: http://localhost:8000"
	@echo "   Frontend UI: http://localhost:5173"
	@echo ""
	@echo "📋 To view logs:"
	@echo "   Backend logs:  docker compose logs backend -f"
	@echo "   Frontend logs: docker compose logs frontend -f"
	@echo ""
	@echo "🛑 To stop the application:"
	@echo "   make down"
up: run

stop: down

down:
	cd docker && docker compose down