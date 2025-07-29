# L{CORE} Frontend - Community IoT Dashboard

A privacy-preserving IoT data marketplace powered by **Cartesi rollups** and **Locale Network**. Built with React, TypeScript, and the Locale Network design system.

![L{CORE} Dashboard](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![TypeScript](https://img.shields.io/badge/TypeScript-5.2-blue)
![React](https://img.shields.io/badge/React-18.2-blue)
![Cartesi](https://img.shields.io/badge/Cartesi-1.5-purple)

## Features

### Core Features
- **Real-time Data Flow**: Live visualization of IoT data processing through Cartesi rollups
- **Device Simulator**: Interactive IoT device simulator with multiple sensor types
- **Community Metrics**: Aggregated analytics without compromising privacy
- **Blockchain Verification**: Fraud-proof guarantees with ZK proofs
- **Privacy-First Design**: End-to-end encryption with dual encryption layers

### Design System
- **Locale Network Branding**: Custom Tailwind theme with brand colors
- **Responsive Design**: Mobile-first approach with enterprise-grade UI
- **Accessibility**: WCAG 2.1 AA compliant components
- **Animations**: Smooth Framer Motion animations for data flow visualization

### Integrations
- **Cartesi GraphQL**: Real-time data fetching from Railway deployment
- **Wallet Connection**: MetaMask integration via RainbowKit
- **Locale Network**: Native support for custom Arbitrum Orbit chain

## Quick Start

### Prerequisites
- **Node.js**: v20+ 
- **npm**: Latest version
- **Git**: Latest version

### Installation

```bash
# 1. Clone and navigate to frontend
cd lcore-frontend

# 2. Install dependencies
npm install

# 3. Configure environment variables
cp .env.example .env
# Edit .env with your WalletConnect Project ID and network settings

# 4. Generate GraphQL types (optional - will auto-generate)
npm run codegen

# 5. Start development server
npm run dev
```

The application will be available at `http://localhost:3000`

## Environment Configuration

Create a `.env` file with these variables:

```bash
# WalletConnect Project ID (get from https://cloud.walletconnect.com/)
VITE_WALLET_CONNECT_PROJECT_ID=your_project_id_here

# Locale Network RPC
VITE_LOCALE_NETWORK_RPC=https://kcchain-api.up.railway.app

# Cartesi GraphQL Endpoint  
VITE_CARTESI_GRAPHQL=https://lcore-iot-node-production.up.railway.app/graphql

# Contract Addresses (Locale Network v1.8)
VITE_INPUT_BOX_ADDRESS=0xC1f612D9ad2270e31BF41fAdBb92f79B63649133
VITE_CARTESI_DAPP_ADDRESS=0xB7B462b81A10A24e1976C9029Ef8FfBdCFc1a96a
```

## Architecture

### Component Structure
```
src/
├── components/
│   ├── Layout/           # Navigation and layout components
│   └── Dashboard/        # Dashboard-specific components
├── pages/                # Route-based page components
├── types/                # TypeScript type definitions
├── config/               # Configuration and constants
└── lib/                  # Utilities and API clients
```

### Key Components

#### RealTimeDataFlow
- **Purpose**: Visualizes live IoT data processing through Cartesi
- **Features**: 4-step animation, GraphQL polling, payload decoding
- **Technology**: Framer Motion, Apollo Client subscriptions

#### DeviceSimulator  
- **Purpose**: Interactive IoT device simulation for testing
- **Features**: 6 sensor types, configurable intervals, real data generation
- **Integration**: Submits to InputBox contract via ethers.js

#### CommunityMetrics
- **Purpose**: Displays aggregated community statistics  
- **Privacy**: No individual device data exposed
- **Metrics**: Active devices, data throughput, earnings, privacy score

## Design System

### Color Palette
```css
/* Locale Network Brand Colors */
--locale-blue: #1B3B6F      /* Primary headers, buttons */
--smart-city-teal: #3AB5C4   /* IoT actions, data viz */
--cloud-white: #F5F7FA       /* Clean backgrounds */
--urban-grey: #A3A8B2        /* Text, neutral elements */
--accent-lime: #C9FF56       /* Success states, CTAs */
--muted-coral: #E89B89       /* Community elements */
--warm-amber: #F5B041        /* User interactions */
```

### Typography
- **Primary**: Inter (headers, body text)
- **Monospace**: IBM Plex Mono (technical data, logs)
- **Hierarchy**: H1 (36px), H2 (24px), Body (16px), Caption (12px)

### Custom Components
```css
.btn-primary        /* Locale blue primary button */
.btn-secondary      /* Outlined secondary button */
.btn-accent         /* Accent lime CTA button */
.locale-card        /* Standard card with accent stripe */
.privacy-indicator  /* Privacy/encryption badges */
.device-card-active /* Active device with lime glow */
```

## API Integration

### GraphQL Queries
The frontend connects to the Cartesi node via GraphQL for real-time data:

```typescript
// Recent inputs from IoT devices
const GET_RECENT_INPUTS = gql`
  query GetRecentInputs($first: Int!) {
    inputs(first: $first, orderBy: TIMESTAMP_DESC) {
      edges {
        node {
          index
          timestamp  
          msgSender
          payload
        }
      }
    }
  }
`;
```

### Blockchain Integration
- **InputBox Contract**: Submit IoT data via `addInput()`
- **Cartesi DApp**: Query processed data and execute vouchers
- **Device Registry**: Manage device ownership and permissions

## Development

### Available Scripts
```bash
npm run dev        # Start development server
npm run build      # Build for production  
npm run preview    # Preview production build
npm run lint       # Run ESLint
npm run codegen    # Generate GraphQL types
```

### Key Technologies
- **React 18**: Modern React with concurrent features
- **TypeScript 5**: Full type safety
- **Vite**: Fast development and optimized builds
- **Tailwind CSS**: Utility-first styling with custom theme
- **Apollo Client**: GraphQL state management with subscriptions
- **Framer Motion**: Smooth animations and transitions
- **Lucide React**: Consistent icon library
- **RainbowKit**: Wallet connection UI

## Deployment

### Production Build
```bash
npm run build
```

The `dist/` folder contains the optimized production build.

### Deployment Platforms
- **Vercel**: Recommended for optimal performance
- **Netlify**: Full static site hosting  
- **Railway**: If you need server-side features
- **IPFS**: Decentralized hosting option

### Environment Variables
Production deployments require the same environment variables as development. Most platforms support `.env` file uploads or environment variable configuration via UI.

## Live Demo

**Production URL**: Coming soon  
**GraphQL Endpoint**: https://lcore-iot-node-production.up.railway.app/graphql  
**Locale Network**: Custom Arbitrum Orbit chain

## Privacy & Security

### Privacy-First Design
- **No Location Data**: Zero geographic information collected
- **Dual Encryption**: AES-256-GCM + XChaCha20-Poly1305  
- **ZK Proofs**: Privacy-preserving verification via Cartesi
- **Community Focus**: Equal access, no municipal privileges

### Security Features
- **Fraud-Proof**: Cartesi rollups provide mathematical guarantees
- **Deterministic Processing**: Reproducible computations in RISC-V VM
- **On-Chain Verification**: All data processing verifiable on Locale Network

## Contributing

1. **Fork** the repository
2. **Clone** your fork: `git clone <your-fork-url>`
3. **Install** dependencies: `npm install`
4. **Create** feature branch: `git checkout -b feature/amazing-feature`
5. **Commit** changes: `git commit -m 'Add amazing feature'`
6. **Push** branch: `git push origin feature/amazing-feature`
7. **Open** pull request

### Development Guidelines
- Follow the existing code style and component patterns
- Use TypeScript for all new code
- Include proper error handling and loading states
- Test components with various data scenarios
- Maintain the Locale Network design system

## Support

- **Documentation**: See `/L{CORE}_FRONTEND_DEVELOPMENT_PLAN.md`
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Contact**: Modern Society Labs team

## License

MIT License - see [LICENSE](../LICENSE) file for details.

---

**Built with love by Modern Society Labs**  
*Empowering communities through privacy-preserving IoT data sharing* 