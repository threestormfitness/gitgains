# GitGains

A Retrieval-Augmented Generation (RAG) system for intelligent workout programming, combining structured training data with AI to create personalized, evidence-based fitness programs.

## 🎯 Vision

GitGains bridges the gap between human expertise and AI capabilities in exercise programming. By structuring and indexing training methodologies from diverse sources - scientific literature, experienced coaches, and real-world practitioners - GitGains enables AI to generate programs that are both evidence-based and practically tested.

Our approach combines:
- **Structured Knowledge**: Systematic organization of training principles
- **Flexible Implementation**: Adaptable to different training contexts
- **AI Enhancement**: RAG-powered program generation
- **Time Efficiency**: Built-in time management for realistic programming
- **Evidence-Based Practice**: Grounded in research and real-world experience

## 🧠 How It Works

GitGains uses a RAG (Retrieval-Augmented Generation) architecture:
1. **Retrieval**: Vector database searches across training modules, exercise substitutions, and programming parameters
2. **Augmentation**: Combines retrieved knowledge with context-specific requirements
3. **Generation**: Creates personalized programs using both stored knowledge and AI capabilities

## 🏗️ Project Structure

```
gitgains/
├── data/
│   ├── db/                # Vector database storage
│   ├── loading_modules/   # Set/rep schemes and progression
│   ├── exercise_substitutions/  # Movement alternatives
│   ├── program_parameters/      # Programming strategies
│   └── master_lists/     # Reference taxonomies
├── docs/                 # Documentation and guides
├── prompts/             # AI interaction templates
└── scripts/
    ├── database/        # Vector DB implementation
    └── program_generator.py  # AI program generation
```

## 🚀 Features

- **Vector Database**: Local Chroma DB for efficient knowledge retrieval
- **Flexible Data Structure**: JSON-based definitions with automatic normalization
- **Rich Documentation**: Markdown files explaining methodologies
- **OpenAI Integration**: GPT-4 powered program generation
- **Data Normalization**: Automatic standardization of time, load, and other parameters
- **Cross-Reference System**: Links between exercises, progressions, and substitutions

## 🛠️ Getting Started

1. **Setup Environment**:
   ```bash
   cd scripts/database
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure API**:
   - Add OpenAI API key to `.env`
   - Review database configuration

3. **Load Data**:
   ```bash
   python load_all_data.py
   ```

4. **Generate Programs**:
   ```bash
   python program_generator.py
   ```

See [database_implementation.md](docs/database_implementation.md) for detailed setup instructions.

## 🤝 Contributing

We welcome contributions in various forms:
- **Training Modules**: Set/rep schemes and progression strategies
- **Exercise Data**: Movement patterns and substitutions
- **Programming Logic**: Periodization and progression algorithms
- **Code Improvements**: Database and AI integration enhancements

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📖 Documentation

- [Project Overview](docs/project_overview.md): High-level system design
- [Database Implementation](docs/database_implementation.md): Technical details
- [API Integration](docs/api_integration.md): Working with AI services

## 🔧 Technical Stack

- **Database**: Chroma (vector database)
- **AI Integration**: OpenAI GPT-4
- **Data Format**: JSON with Markdown documentation
- **Language**: Python 3.8+
- **Key Libraries**: 
  - `chromadb`: Vector database
  - `langchain`: LLM integration
  - `pydantic`: Data validation
  - `openai`: GPT-4 API

## 📝 License

[LICENSE](LICENSE)

## 🎯 Roadmap

- [ ] Web interface for program generation
- [ ] Additional training methodologies and parameters
- [ ] Enhanced periodization strategies
- [ ] Mobile app integration
- [ ] Community contribution platform