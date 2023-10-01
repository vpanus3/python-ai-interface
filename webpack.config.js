const path = require('path');

module.exports = {
  // Entry point for your application
  entry: './src/index.js',

  // Output configuration
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'static', 'dist')
  },

  // Devtool configuration for Source Maps
  devtool: 'eval-source-map',  // This line generates Source Maps

  // Module configuration
  module: {
    rules: [
      // Babel loader for React JSX and ES6+ syntax
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react']
          }
        }
      },
      // CSS loader for Bootstrap and your own CSS
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      },
      // File loader for FontAwesome
      {
        test: /\.(woff(2)?|ttf|eot|svg)(\?v=\d+\.\d+\.\d+)?$/,
        use: [
          {
            loader: 'file-loader',
            options: {
              name: '[name].[ext]',
              outputPath: 'fonts/'
            }
          }
        ]
      }
    ]
  },
  resolve: {
    extensions: ['.js', '.jsx']
  },
};
