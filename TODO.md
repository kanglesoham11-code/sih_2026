# ORCA Development TODO List

**Last Updated:** September 10, 2026  
**Priority Legend:** 🔴 Critical | 🟡 High | 🟢 Medium | 🔵 Low

---

## 🔴 CRITICAL - Required for MVP

### 1. Complete Source Adapters
**Priority:** 🔴 Critical  
**Estimated Time:** 2-3 weeks  
**Assignee:** Backend Developer

- [ ] **INCOIS ERDDAP** (`backend/app/connectors/incois_erddap.py`)
  - [ ] Implement `get_subset()` with actual ERDDAP queries
  - [ ] Add dataset discovery logic
  - [ ] Parse NetCDF/CSV responses
  - [ ] Normalize to Payload format
  - [ ] Add error handling
  - [ ] Test with real API

- [ ] **IMD Weather** (`backend/app/connectors/imd_weather.py`)
  - [ ] Verify actual IMD API endpoints
  - [ ] Implement authentication flow
  - [ ] Complete `get_latest()` implementation
  - [ ] Complete `get_forecast()` implementation
  - [ ] Complete `get_warnings()` implementation
  - [ ] Parse real response formats
  - [ ] Test with live data

- [ ] **Copernicus Marine** (`backend/app/connectors/copernicus_marine.py`)
  - [ ] Complete SDK integration
  - [ ] Implement `_parse_xarray_to_payloads()` properly
  - [ ] Handle authentication errors
  - [ ] Add dataset caching
  - [ ] Test with real SDK calls

### 2. LLM Integration
**Priority:** 🔴 Critical  
**Estimated Time:** 1 week  
**Assignee:** AI/ML Engineer

- [ ] **OpenAI Integration** (`backend/app/agents/`)
  - [ ] Implement `_call_llm()` in BaseAgent
  - [ ] Add conversation memory/context
  - [ ] Implement prompt templates
  - [ ] Handle API errors and rate limits
  - [ ] Add response streaming

- [ ] **Conversation Agent** (`backend/app/agents/conversation.py`)
  - [ ] Implement LLM-based intent classification
  - [ ] Implement entity extraction with LLM
  - [ ] Add conversation context management
  - [ ] Test intent detection accuracy

- [ ] **Planner Agent** (`backend/app/agents/planner.py`)
  - [ ] Implement LLM-based task decomposition
  - [ ] Add mode determination logic
  - [ ] Test planning with complex queries

### 3. Wire Up API Endpoints
**Priority:** 🔴 Critical  
**Estimated Time:** 1-2 weeks  
**Assignee:** Backend Developer

- [ ] **Connect Dependencies** (`backend/app/api/endpoints.py`)
  - [ ] Uncomment dependency injection
  - [ ] Wire gateway to endpoints
  - [ ] Wire freshness manager to endpoints
  - [ ] Wire agent orchestrator to /chat

- [ ] **Implement Endpoints**
  - [ ] `/data/latest` - Complete implementation
  - [ ] `/data/subset` - Complete implementation
  - [ ] `/chat` - Wire to agent orchestrator
  - [ ] `/pfz/forecast` - Implement PFZ logic
  - [ ] `/warnings` - Aggregate warnings from sources
  - [ ] `/sources` - List registered sources
  - [ ] `/freshness/report` - Wire to freshness manager

- [ ] **Add Error Handling**
  - [ ] Validation errors (400)
  - [ ] Authentication errors (401)
  - [ ] Authorization errors (403)
  - [ ] Not found errors (404)
  - [ ] Rate limit errors (429)
  - [ ] Server errors (500)

---

## 🟡 HIGH PRIORITY - Essential Features

### 4. Authentication System
**Priority:** 🟡 High  
**Estimated Time:** 1 week  
**Assignee:** Backend Developer

- [ ] **JWT Implementation** (`backend/app/core/security.py` - create file)
  - [ ] Token generation
  - [ ] Token validation
  - [ ] Refresh token logic
  - [ ] Token expiration handling

- [ ] **User Management**
  - [ ] Registration endpoint
  - [ ] Login endpoint
  - [ ] Password hashing (bcrypt)
  - [ ] Email verification
  - [ ] Password reset

- [ ] **Authorization**
  - [ ] Role-based access control (RBAC)
  - [ ] Permission checks
  - [ ] Admin-only endpoints

### 5. Frontend MVP
**Priority:** 🟡 High  
**Estimated Time:** 2-3 weeks  
**Assignee:** Frontend Developer

- [ ] **Project Setup** (`frontend/` - to be created)
  - [ ] Initialize Next.js 14+ project
  - [ ] Configure TypeScript
  - [ ] Set up Tailwind CSS
  - [ ] Configure environment variables
  - [ ] Set up API client (axios/fetch)

- [ ] **Core Components**
  - [ ] Layout with header/footer
  - [ ] Navigation menu
  - [ ] Loading states
  - [ ] Error boundaries
  - [ ] Toast notifications

- [ ] **Chat Interface** (`frontend/app/chat/`)
  - [ ] Chat input component
  - [ ] Message list component
  - [ ] Message bubbles (user/agent)
  - [ ] Typing indicator
  - [ ] Markdown rendering
  - [ ] Code highlighting

- [ ] **Map Component** (`frontend/components/Map/`)
  - [ ] MapLibre GL JS integration
  - [ ] Layer controls
  - [ ] Marker placement
  - [ ] Popup information
  - [ ] Drawing tools (optional)

- [ ] **Dashboard** (`frontend/app/dashboard/`)
  - [ ] System health display
  - [ ] Source status cards
  - [ ] Recent queries
  - [ ] Quick actions

### 6. Testing Framework
**Priority:** 🟡 High  
**Estimated Time:** 2 weeks  
**Assignee:** QA Engineer / Backend Developer

- [ ] **Unit Tests** (`backend/tests/unit/`)
  - [ ] Test utilities (geospatial, validators)
  - [ ] Test data models
  - [ ] Test connectors (with mocks)
  - [ ] Test agents (with mocks)
  - [ ] Test services (gateway, freshness)

- [ ] **Integration Tests** (`backend/tests/integration/`)
  - [ ] Test API endpoints
  - [ ] Test database operations
  - [ ] Test Celery tasks
  - [ ] Test agent orchestration

- [ ] **Test Configuration**
  - [ ] pytest configuration
  - [ ] Test fixtures
  - [ ] Mock data generators
  - [ ] Coverage reporting (aim for 70%+)

---

## 🟢 MEDIUM PRIORITY - Enhanced Features

### 7. Additional Agents
**Priority:** 🟢 Medium  
**Estimated Time:** 1-2 weeks  
**Assignee:** AI/ML Engineer

- [ ] **Geospatial Agent** (`backend/app/agents/geospatial.py`)
  - [ ] EEZ boundary checking
  - [ ] MPA detection
  - [ ] Distance calculations
  - [ ] Coordinate transformations

- [ ] **Risk Assessment Agent** (`backend/app/agents/risk_assessment.py`)
  - [ ] Warning aggregation
  - [ ] Risk scoring algorithm
  - [ ] Safety recommendations
  - [ ] Alert prioritization

- [ ] **Route Optimization Agent** (`backend/app/agents/route_optimization.py`)
  - [ ] Path finding algorithm
  - [ ] Weather integration
  - [ ] Fuel optimization
  - [ ] ETA calculation

### 8. More Source Adapters
**Priority:** 🟢 Medium  
**Estimated Time:** 2-3 weeks  
**Assignee:** Backend Developer

- [ ] **Global Fishing Watch** (`backend/app/connectors/gfw.py`)
  - [ ] API authentication
  - [ ] Vessel tracking
  - [ ] Fishing activity data
  - [ ] AIS data integration

- [ ] **OBIS** (`backend/app/connectors/obis.py`)
  - [ ] Species occurrence data
  - [ ] Biodiversity metrics
  - [ ] Spatial queries
  - [ ] Taxonomy integration

- [ ] **Protected Planet** (`backend/app/connectors/protected_planet.py`)
  - [ ] MPA boundaries
  - [ ] Protection level info
  - [ ] Restriction data
  - [ ] License compliance

- [ ] **Argo Floats** (`backend/app/connectors/argo.py`)
  - [ ] Profile data
  - [ ] Temperature/salinity
  - [ ] Subsurface conditions
  - [ ] Float tracking

### 9. PFZ Forecasting Algorithm
**Priority:** 🟢 Medium  
**Estimated Time:** 2 weeks  
**Assignee:** Data Scientist / ML Engineer

- [ ] **Algorithm Development** (`backend/app/services/pfz_forecast.py`)
  - [ ] Research PFZ methodologies
  - [ ] Define input parameters
  - [ ] Implement suitability scoring
  - [ ] Add temporal forecasting
  - [ ] Species-specific logic

- [ ] **Integration**
  - [ ] Connect to PFZ Intelligence Agent
  - [ ] Store forecasts in database
  - [ ] Schedule daily generation
  - [ ] Create visualization data

---

## 🔵 LOW PRIORITY - Polish & Scale

### 10. Performance Optimization
**Priority:** 🔵 Low  
**Estimated Time:** 1-2 weeks  
**Assignee:** Backend Developer

- [ ] **Database Optimization**
  - [ ] Add indexes on frequently queried columns
  - [ ] Optimize slow queries (EXPLAIN ANALYZE)
  - [ ] Implement connection pooling
  - [ ] Add query result caching

- [ ] **API Optimization**
  - [ ] Enable response compression (gzip)
  - [ ] Implement Redis caching
  - [ ] Add CDN for static assets
  - [ ] Optimize serialization

- [ ] **Background Tasks**
  - [ ] Monitor task execution time
  - [ ] Optimize slow tasks
  - [ ] Implement task prioritization
  - [ ] Add result caching

### 11. Monitoring & Observability
**Priority:** 🔵 Low  
**Estimated Time:** 1 week  
**Assignee:** DevOps Engineer

- [ ] **Metrics** (`backend/app/core/metrics.py`)
  - [ ] Prometheus integration
  - [ ] Custom metrics (requests, latency, errors)
  - [ ] Source health metrics
  - [ ] Agent performance metrics

- [ ] **Dashboards** (`monitoring/grafana/`)
  - [ ] System overview dashboard
  - [ ] API performance dashboard
  - [ ] Source health dashboard
  - [ ] Agent performance dashboard

- [ ] **Alerting**
  - [ ] Source down alerts
  - [ ] High error rate alerts
  - [ ] Slow response alerts
  - [ ] Disk/memory alerts

- [ ] **Error Tracking**
  - [ ] Sentry integration
  - [ ] Error grouping
  - [ ] Error notifications
  - [ ] Stack trace capture

### 12. Deployment & DevOps
**Priority:** 🔵 Low  
**Estimated Time:** 1-2 weeks  
**Assignee:** DevOps Engineer

- [ ] **Containerization**
  - [ ] Production Dockerfile
  - [ ] Docker Compose for prod
  - [ ] Image optimization
  - [ ] Multi-stage builds

- [ ] **Kubernetes** (`k8s/`)
  - [ ] Deployment manifests
  - [ ] Service definitions
  - [ ] Ingress configuration
  - [ ] ConfigMaps and Secrets

- [ ] **CI/CD** (`.github/workflows/`)
  - [ ] Test pipeline
  - [ ] Build pipeline
  - [ ] Deploy pipeline
  - [ ] Rollback procedure

- [ ] **Infrastructure**
  - [ ] Terraform/IaC scripts
  - [ ] Database backups
  - [ ] Disaster recovery plan
  - [ ] Monitoring setup

---

## 📝 Documentation Updates

### Ongoing Documentation
- [ ] Keep API.md updated with new endpoints
- [ ] Update PROJECT_STATUS.md as features complete
- [ ] Document new source adapters
- [ ] Add deployment guide
- [ ] Create user manual
- [ ] Write contributor guidelines

---

## 🧪 Quality Assurance

### Before Production
- [ ] **Security Audit**
  - [ ] Penetration testing
  - [ ] Dependency vulnerability scan
  - [ ] Code security review
  - [ ] OWASP Top 10 check

- [ ] **Load Testing**
  - [ ] API endpoint load tests
  - [ ] Database stress tests
  - [ ] Celery worker capacity tests
  - [ ] Concurrent user simulation

- [ ] **User Acceptance Testing**
  - [ ] Test all user scenarios
  - [ ] Verify data accuracy
  - [ ] Check mobile responsiveness
  - [ ] Accessibility audit (WCAG 2.1)

---

## 🎯 Milestones

### Milestone 1: Core Functionality (4 weeks)
- ✅ Project structure
- ✅ Database models
- ✅ Basic agents
- 🔴 Complete source adapters
- 🔴 LLM integration
- 🔴 Working API endpoints

**Goal:** Functional backend with live data

### Milestone 2: User Interface (3 weeks)
- 🟡 Frontend setup
- 🟡 Chat interface
- 🟡 Map component
- 🟡 Dashboard
- 🟡 Authentication

**Goal:** Usable web application

### Milestone 3: Testing & QA (2 weeks)
- 🟡 Unit tests (70% coverage)
- 🟡 Integration tests
- 🟢 Security audit
- 🟢 Load testing

**Goal:** Stable, tested system

### Milestone 4: Advanced Features (3 weeks)
- 🟢 Additional agents
- 🟢 More source adapters
- 🟢 PFZ forecasting
- 🟢 Route optimization

**Goal:** Feature-complete system

### Milestone 5: Production Ready (2 weeks)
- 🔵 Performance optimization
- 🔵 Monitoring setup
- 🔵 Deployment pipeline
- 🔵 Documentation complete

**Goal:** Deployed to production

---

## 📅 Recommended Schedule

### Sprint 1 (Weeks 1-2): Core Data Flow
Focus: Get live data flowing through the system
- Complete INCOIS ERDDAP adapter
- Implement basic LLM integration
- Wire up /chat endpoint
- Test end-to-end agent conversation

### Sprint 2 (Weeks 3-4): Multi-Source Integration
Focus: Add more data sources
- Complete IMD Weather adapter
- Finish Copernicus Marine integration
- Test data aggregation
- Implement caching

### Sprint 3 (Weeks 5-6): User Interface
Focus: Build frontend
- Set up Next.js project
- Create chat interface
- Add map component
- Integrate with backend

### Sprint 4 (Weeks 7-8): Testing & Polish
Focus: Quality assurance
- Write tests
- Fix bugs
- Optimize performance
- Security review

### Sprint 5 (Weeks 9-10): Advanced Features
Focus: Enhanced capabilities
- Implement PFZ forecasting
- Add route optimization
- Build admin features
- Add notifications

### Sprint 6 (Weeks 11-12): Deployment
Focus: Go live
- Production configuration
- Deploy to staging
- User acceptance testing
- Deploy to production

---

## 🔗 Quick Links

- [Development Guide](docs/DEVELOPMENT.md)
- [API Documentation](docs/API.md)
- [Project Status](PROJECT_STATUS.md)
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md)
- [Quick Start](docs/QUICKSTART.md)

---

**Remember:** This is a living document. Update it as you complete tasks and add new ones!
