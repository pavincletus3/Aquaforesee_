# AquaForesee Frontend

React.js frontend application for the AquaForesee water resource management system.

## Features

- Interactive dashboard with real-time data visualization
- Leaflet-based maps with district-level water stress indicators
- Chart.js visualizations for trends and analytics
- Scenario simulation with adjustable parameters
- PDF report generation and data export
- Responsive design with Tailwind CSS

## Technology Stack

- **React 18** - Modern React with hooks
- **Tailwind CSS** - Utility-first CSS framework
- **Leaflet** - Interactive maps
- **Chart.js** - Data visualization
- **Axios** - HTTP client
- **React Router** - Client-side routing

## Quick Start

1. **Install dependencies**

```bash
npm install
```

2. **Set environment variables**

```bash
# Create .env file
REACT_APP_API_URL=http://localhost:8000
```

3. **Start development server**

```bash
npm start
```

4. **Open browser**
   Navigate to http://localhost:3000

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run test suite
- `npm run eject` - Eject from Create React App

## Project Structure

```
src/
├── components/          # React components
│   ├── Dashboard.js     # Main dashboard
│   ├── LoginPage.js     # Authentication
│   ├── Header.js        # Navigation header
│   ├── Sidebar.js       # Control panel
│   ├── MapView.js       # Interactive map
│   ├── ChartsPanel.js   # Data visualizations
│   ├── SummaryPanel.js  # Export and summary
│   └── LoadingSpinner.js # Loading states
├── context/             # React context providers
│   └── AuthContext.js   # Authentication state
├── services/            # API and external services
│   └── api.js          # API client
├── App.js              # Main application component
├── index.js            # Application entry point
└── index.css           # Global styles
```

## Key Components

### Dashboard

Main application interface with:

- Interactive map showing water stress levels
- Control sidebar for scenario parameters
- Charts panel with trend analysis
- Summary panel with export functionality

### MapView

Leaflet-based map component featuring:

- District boundaries with color-coded stress levels
- Interactive popups with detailed information
- Legend and zoom controls
- Real-time updates based on scenario changes

### ChartsPanel

Data visualization component with:

- Line chart: Historical demand vs supply trends
- Bar chart: Top 5 water-stressed districts
- Doughnut chart: Stress level distribution

### SummaryPanel

Export and summary functionality:

- PDF report generation with jsPDF
- CSV data export
- Key insights and recommendations
- Scenario parameter summary

## Styling

The application uses Tailwind CSS with custom configurations:

- **Color Palette**: Water-themed blues and stress-level colors
- **Components**: Reusable button, card, and input styles
- **Responsive**: Mobile-first design approach
- **Animations**: Subtle transitions and loading states

## State Management

- **React Context** for authentication state
- **Local State** with useState for component data
- **API State** managed through custom hooks
- **Loading States** for better user experience

## API Integration

The frontend communicates with the backend through:

- RESTful API calls using Axios
- Error handling with user-friendly messages
- Loading states during API requests
- Automatic retry for failed requests

## Testing

Run tests with:

```bash
npm test
```

Test coverage includes:

- Component rendering
- User interactions
- API integration
- Error handling

## Deployment

### Development Build

```bash
npm run build
```

### Docker Deployment

```bash
docker build -t aquaforesee-frontend .
docker run -p 3000:3000 aquaforesee-frontend
```

### Production Deployment

1. Build the application: `npm run build`
2. Serve static files with nginx or similar
3. Configure environment variables for production API
4. Set up HTTPS and security headers

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance Optimizations

- Code splitting with React.lazy
- Image optimization
- Bundle size optimization
- Efficient re-rendering with React.memo
- Debounced API calls for scenario changes

## Contributing

1. Follow React best practices
2. Use functional components with hooks
3. Maintain consistent styling with Tailwind
4. Add tests for new components
5. Ensure responsive design
