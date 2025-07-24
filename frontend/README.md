# Impromptu Frontend

A modern, responsive web application for AI-powered social matching built with Next.js, React, and Tailwind CSS.

## ✨ Features

- 🎨 **Dual Theme System**: Switch between Romantic Mode (pink theme) and Team Mode (miami blue theme)
- 🌍 **Internationalization**: Support for Chinese and English languages
- 🌙 **Dark/Light Mode**: Complete theme switching capability
- 📱 **Responsive Design**: Mobile-first design that works on all devices
- 🎯 **AI-Powered Matching**: Advanced compatibility analysis for both romantic and team matching
- 👤 **User Profiles**: Comprehensive profile management with preferences
- 💬 **Real-time Chat**: AI assistant and user-to-user messaging
- 🔔 **Admin Dashboard**: Complete backend management system
- 🛡 **Type Safety**: Full TypeScript implementation

## 🏗 Tech Stack

- **Framework**: Next.js 14 with App Router
- **UI Library**: React 18
- **Styling**: Tailwind CSS with custom theme system
- **Components**: Radix UI primitives with custom styling
- **Icons**: Lucide React
- **State Management**: Zustand
- **Theme Management**: next-themes
- **TypeScript**: Full type safety

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js app router pages
│   ├── globals.css        # Global styles and theme variables
│   ├── layout.tsx         # Root layout with providers
│   ├── page.tsx           # Homepage - matching dashboard
│   ├── login/             # Authentication pages
│   ├── romantic/          # Romantic matching mode
│   ├── team/              # Team matching mode
│   ├── chat/              # Chat interface
│   ├── profile/           # User profile management
│   └── admin/             # Admin dashboard
├── components/            # Reusable components
│   ├── ui/               # Base UI components (shadcn/ui style)
│   │   ├── button.tsx    # Button component
│   │   ├── card.tsx      # Card component
│   │   ├── input.tsx     # Input component
│   │   ├── avatar.tsx    # Avatar component
│   │   ├── badge.tsx     # Badge component
│   │   ├── progress.tsx  # Progress component
│   │   └── ...           # Other UI components
│   ├── chat-interface.tsx # Chat component
│   ├── navbar.tsx        # Navigation bar
│   ├── mode-switcher.tsx # Floating mode switcher
│   ├── theme-provider.tsx # Theme context provider
│   ├── loading-spinner.tsx # Loading animation
│   └── empty-state.tsx   # Empty state component
├── lib/                  # Utilities and configuration
│   ├── utils.ts          # Utility functions
│   └── store.ts          # Zustand state management
└── public/               # Static assets
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18.0 or later
- npm or yarn package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Create environment variables file:
```bash
cp .env.example .env.local
```

4. Run the development server:
```bash
npm run dev
# or
yarn dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🎨 Theme System

The application features a sophisticated dual-theme system:

### Romantic Mode
- **Primary Colors**: Pink gradient (#ec4899 to #be185d)
- **Use Case**: Dating and romantic relationship matching
- **Visual Style**: Warm, inviting, and emotionally engaging
- **Icon**: Heart ❤️

### Team Mode
- **Primary Colors**: Miami Blue gradient (#0ea5e9 to #0369a1)
- **Use Case**: Professional team building and collaboration
- **Visual Style**: Modern, tech-focused, and professional
- **Icon**: Users 👥

### Theme Switching
- **Mode Switcher**: Floating sidebar component for easy theme switching
- **Automatic Styling**: All components automatically adapt to the selected theme
- **Persistent State**: Theme preference is maintained across sessions

## 📱 Pages & Features

### 🏠 Homepage (`/`)
- **Dashboard Overview**: Display matching tasks and progress
- **Search & Filter**: Find specific matching tasks
- **Progress Tracking**: Visual progress indicators
- **Quick Actions**: Create new matching tasks

### 💕 Romantic Mode (`/romantic`)
- **Personality Analysis**: Big Five personality traits visualization
- **Matching Preferences**: Age range, interests, values compatibility
- **Recent Matches**: Latest romantic matches with compatibility scores
- **Profile Actions**: Start new matches, complete profile

### 👥 Team Mode (`/team`)
- **Skills Analysis**: Technical and soft skills assessment
- **Team Preferences**: Size, work mode, project type
- **Team Recommendations**: Suggested teams with skill gaps
- **Project Categories**: Browse by development, design, business, research

### 💬 Chat (`/chat`)
- **AI Assistant**: Intelligent matching optimization
- **User Messaging**: Real-time conversations with matches
- **Voice Support**: Voice message recording (UI ready)
- **Message History**: Persistent chat history

### 👤 Profile (`/profile`)
- **Personal Information**: Name, contact, location, bio
- **Interests Management**: Tag-based interest system
- **Privacy Controls**: Public profile, notifications, mode preferences
- **Account Stats**: Credits, subscription, match count

### 🔐 Authentication (`/login`)
- **Email/Password**: Traditional authentication
- **Social Login**: Google and Facebook integration (UI ready)
- **Registration**: New user account creation
- **Responsive Design**: Mobile-optimized forms

### 🛡 Admin Dashboard (`/admin`)
- **User Management**: View and manage user accounts
- **Content Moderation**: Review user-generated content
- **Analytics Dashboard**: System statistics and metrics
- **System Settings**: Configuration management

## 🎯 Key Components

### Navbar
- **Dynamic Branding**: Logo changes based on theme mode
- **Navigation Links**: Active state indication
- **User Menu**: Profile, messages, credits, subscriptions
- **Utility Actions**: Language switch, theme toggle
- **Mobile Responsive**: Collapsible navigation

### Mode Switcher
- **Fixed Positioning**: Always accessible floating sidebar
- **Visual Feedback**: Active state with proper colors
- **Smooth Transitions**: Animated theme changes
- **Accessibility**: Proper ARIA labels

### Chat Interface
- **Real-time Messaging**: Instant message exchange
- **AI Integration**: Smart assistant responses
- **Rich Media Support**: Text, voice, emoji (UI ready)
- **Typing Indicators**: Loading states and animations

## 🔧 Customization

### Adding New Themes
1. Define color variables in `globals.css`
2. Add theme class to Tailwind configuration
3. Update `ThemeProvider` component
4. Add theme option to store

### Extending UI Components
All UI components follow the shadcn/ui pattern:
- Modify base styles in component files
- Use `cn()` utility for conditional styling
- Leverage Tailwind's utility classes
- Maintain accessibility standards

## 🌐 Internationalization

The app supports multiple languages:
- **Chinese (zh)** - Default language
- **English (en)** - Secondary language
- **Language Switching**: Navbar toggle button
- **Content Localization**: All text content is externalized
- **Date/Time Formatting**: Locale-aware formatting

## 📊 State Management

Using Zustand for lightweight state management:

```typescript
interface AppState {
  themeMode: 'romantic' | 'team'
  isDarkMode: boolean
  language: 'zh' | 'en'
  user: User | null
  // Actions
  setThemeMode: (mode: ThemeMode) => void
  toggleDarkMode: () => void
  setLanguage: (lang: 'zh' | 'en') => void
  setUser: (user: User) => void
}
```

## 🎭 Development Guidelines

### Code Style
- Use TypeScript for all new files
- Follow React best practices and hooks patterns
- Implement responsive design patterns
- Use semantic HTML elements
- Maintain accessibility compliance (WCAG 2.1)

### Component Structure
- Keep components small and focused (single responsibility)
- Use proper TypeScript interfaces for props
- Implement proper error boundaries
- Follow accessibility guidelines
- Use meaningful component and prop names

### Performance Optimization
- Lazy load pages and heavy components
- Optimize images and assets
- Minimize bundle size
- Use proper caching strategies
- Implement efficient re-renders

## 🚀 Deployment

### Build for Production
```bash
npm run build
npm start
```

### Environment Variables
Required environment variables:
- `NEXT_PUBLIC_API_URL`: Backend API endpoint
- `NEXTAUTH_SECRET`: Authentication secret
- `NEXTAUTH_URL`: Application URL

### Docker Support
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 🧪 Testing

### Running Tests
```bash
npm run test        # Run unit tests
npm run test:e2e    # Run end-to-end tests
npm run test:watch  # Watch mode
```

### Testing Strategy
- **Unit Tests**: Component logic and utilities
- **Integration Tests**: Page-level functionality
- **E2E Tests**: Complete user workflows
- **Accessibility Tests**: Screen reader compatibility

## 🤝 Contributing

1. Follow the established code style and patterns
2. Write meaningful commit messages
3. Update documentation for new features
4. Test thoroughly across different devices and browsers
5. Ensure accessibility compliance
6. Consider internationalization for new text content

## 📄 License

This project is proprietary and confidential.

---

For additional support or questions, please refer to the API documentation or contact the development team. 