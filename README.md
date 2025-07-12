# 🎯 10,000 Hour Mastery Tracker

A beautiful, modern web application built with Streamlit to help you track your journey to mastery following the 10,000-hour rule. Monitor your progress, analyze patterns, and stay motivated on your path to expertise.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.46+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 🏠 **Dashboard**
- **Progress Visualization**: Beautiful circular progress rings showing completion percentage
- **Real-time Timer**: Enhanced H:M:S display with start/stop/pause functionality
- **Quick Stats**: Today's hours, weekly progress, and overall statistics
- **Activity Overview**: Visual summary of all your learning activities

### ⏱️ **Advanced Timer**
- **Smart Timer**: Precise tracking with pause/resume capabilities
- **Pomodoro Mode**: Built-in Pomodoro technique support
- **Auto-save**: Automatically saves your sessions to the database
- **Visual Feedback**: Elegant timer display with status indicators

### 📊 **Statistics & Analytics**
- **Comprehensive Charts**: Daily, weekly, and monthly progress visualization
- **Activity Breakdown**: Pie charts and comparisons across activities
- **Calendar Heatmap**: GitHub-style activity tracking
- **Streak Analysis**: Monitor consistency and build habits
- **Milestone Tracking**: Celebrate achievements at 100h, 500h, 1000h+

### 🎯 **Activity Management**
- **Multiple Activities**: Track different skills simultaneously
- **CRUD Operations**: Create, edit, and delete activities
- **Categories & Tags**: Organize your learning goals
- **Progress Tracking**: Individual progress monitoring per activity
- **Color Coding**: Visual distinction between activities

### 📈 **Progress Insights**
- **Velocity Tracking**: Monitor your learning speed
- **Consistency Scores**: Measure habit formation
- **Estimated Completion**: AI-powered completion date predictions
- **Best Day Analysis**: Identify your most productive patterns

### 💾 **Data Management**
- **Export Capabilities**: CSV and text report generation
- **Data Persistence**: SQLite database for reliable storage
- **Manual Entry**: Add sessions retroactively
- **Backup & Restore**: Easy data management

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) - Modern Python web framework
- **Backend**: Python 3.8+
- **Database**: SQLite with SQLAlchemy ORM
- **Visualization**: Plotly for interactive charts
- **Styling**: Custom CSS with beautiful animations
- **Data Processing**: Pandas for analytics

## 🚀 Quick Start

### Prerequisites

```bash
python >= 3.8
pip (Python package manager)
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/10k-hour-tracker.git
cd 10k-hour-tracker
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
streamlit run app.py
```

4. **Open your browser**
```
http://localhost:8501
```

## 📁 Project Structure

```
10k-hour-tracker/
├── app.py                      # Main application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
│
├── assets/
│   └── style.css              # Custom CSS styling with animations
│
├── components/
│   ├── charts.py              # Chart generation functions
│   ├── progress_ring.py       # Circular progress visualizations
│   └── timer.py               # Timer functionality
│
├── database/
│   ├── models.py              # SQLAlchemy database models
│   ├── database.py            # Database connection setup
│   └── crud.py                # Database operations
│
├── pages/
│   ├── 1_⏱️_Timer.py          # Enhanced timer page
│   ├── 2_📊_Statistics.py     # Analytics and charts
│   └── 3_🎯_Activities.py     # Activity management
│
└── utils/
    └── time_helpers.py        # Time calculation utilities
```

## 🎨 Design Features

- **Modern UI**: Clean, professional interface with hover animations
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Color Themes**: Beautiful purple gradient theme with light accents
- **Smooth Animations**: Elegant hover effects and transitions
- **Visual Feedback**: Interactive elements with immediate responses

## 📱 Usage Guide

### Getting Started

1. **Create Your First Activity**
   - Click "Add New Activity" on the dashboard
   - Enter activity name, category, and description
   - Set as main activity for primary tracking

2. **Start Tracking Time**
   - Use the built-in timer for real-time tracking
   - Or manually add time entries for past sessions
   - Take advantage of pause/resume functionality

3. **Monitor Progress**
   - View your progress ring on the dashboard
   - Check daily/weekly statistics
   - Celebrate milestones as you hit them

4. **Analyze Patterns**
   - Visit the Statistics page for detailed insights
   - Use different time filters to analyze periods
   - Export data for external analysis

### Pro Tips

- 🎯 Set one main activity for focused tracking
- ⏰ Use the Pomodoro timer for better focus
- 📊 Check statistics weekly to identify patterns
- 🎉 Celebrate milestones to stay motivated
- 📝 Add notes to sessions for better tracking

## 🧠 The 10,000 Hour Rule

Based on Malcolm Gladwell's research, the 10,000-hour rule suggests that achieving mastery in any field requires approximately 10,000 hours of deliberate practice. This application helps you:

- **Track Progress**: Monitor your journey towards mastery
- **Stay Motivated**: Visual progress indicators keep you engaged
- **Build Habits**: Consistency tracking helps form lasting habits
- **Optimize Learning**: Analytics help you understand your patterns

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Keep functions focused and modular

## 🐛 Bug Reports

If you find a bug, please create an issue with:
- Description of the bug
- Steps to reproduce
- Expected behavior
- Screenshots (if applicable)
- Your environment details

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Malcolm Gladwell** - For the 10,000-hour rule concept
- **Streamlit Team** - For the amazing framework
- **Open Source Community** - For the tools and libraries used

## 📞 Support

If you like this project, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting new features
- 🤝 Contributing to the codebase

---

**Made with ❤️ by Kumar Abhishek for learners and achievers worldwide**

*Track your hours, master your craft, achieve your dreams!* 
