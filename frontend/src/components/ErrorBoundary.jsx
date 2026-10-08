import React from 'react'

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('VERITAS AI Runtime Error caught by ErrorBoundary:', error, errorInfo)
    this.setState({ errorInfo })
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null })
    if (this.props.onReset) {
      this.props.onReset()
    }
  }

  handleReload = () => {
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#080B0A] text-[#F2F5F0] flex items-center justify-center p-6 selection:bg-[#C5F5D5] selection:text-[#080B0A]">
          <div className="max-w-xl w-full p-8 rounded-3xl bg-[#101512] border border-[#F87171]/30 shadow-2xl space-y-6 text-center">
            {/* Error Icon */}
            <div className="w-16 h-16 rounded-2xl bg-[#180E10] border border-[#F87171]/40 text-[#F87171] flex items-center justify-center mx-auto text-2xl font-bold">
              !
            </div>

            <div className="space-y-2">
              <span className="text-xs font-mono text-[#F87171] uppercase tracking-wider">
                APPLICATION RECOVERY
              </span>
              <h2 className="font-editorial text-3xl font-light text-[#F2F5F0]">
                Unexpected Runtime Issue
              </h2>
              <p className="text-sm font-sans text-[#8A9B91] leading-relaxed">
                An unexpected view error occurred while rendering the workspace. You can recover immediately without losing your session.
              </p>
            </div>

            {/* Error Message Snippet */}
            {this.state.error && (
              <div className="p-4 rounded-xl bg-[#080B0A] border border-white/5 text-left text-xs font-mono text-[#F87171] overflow-x-auto max-h-32">
                {this.state.error.toString()}
              </div>
            )}

            {/* Recovery Action Buttons */}
            <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
              <button
                onClick={this.handleReset}
                className="px-6 py-2.5 rounded-full bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] text-xs font-sans font-bold tracking-wide transition-all shadow-md shadow-[#C5F5D5]/10"
              >
                Recover View
              </button>

              {this.props.onLoadDemo && (
                <button
                  onClick={() => {
                    this.handleReset()
                    this.props.onLoadDemo()
                  }}
                  className="px-6 py-2.5 rounded-full border border-[rgba(197,245,213,0.25)] hover:border-[#C5F5D5] bg-[#101512] text-[#C5F5D5] text-xs font-sans font-semibold tracking-wide transition-all"
                >
                  Load Safe Demo Data
                </button>
              )}

              <button
                onClick={this.handleReload}
                className="px-6 py-2.5 rounded-full border border-white/10 hover:border-white/30 text-[#8A9B91] hover:text-[#F2F5F0] text-xs font-sans transition-all"
              >
                Reload Application
              </button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

