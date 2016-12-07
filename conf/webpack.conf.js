var path = require('path');
var webpack = require("webpack");
var CopysWebpackPlugin = require('copy-webpack-plugin');
var ExtractTextPlugin = require('extract-text-webpack-plugin');

var srcPath = path.resolve(__dirname, '../static/src')
module.exports = {
    devtool: "eval",
    entry: {
        "index": './static/src/jsx/index.jsx',
        "components-bundle": [
            'object-assign',
            'redux',
            'events',
            "./static/src/jsx/components/",
        ],
        "bundle": [
            'react-dom',
            'react-addons-linked-state-mixin',
            'react-router',
            "react",
            'react-bootstrap',
            'react-tap-event-plugin',
            "underscore",
            "classnames",
            'es6-promise',
            'isomorphic-fetch',
            
        ],
    },
    output: {
        path:  './static/dest/',
        filename: './js/[name].js'
    },
    resolve: {
        extensions: ['', '.js', '.jsx', ".json"],
        alias: {
            "echarts$": "echarts/dist/echarts.min.js",
            "redux$": "redux/dist/redux.min.js",
            "underscore": "underscore/underscore-min.js",
            'es6-promise': 'es6-promise/dist/es6-promise.min.js',
            '@srcPath': srcPath
            // "react$":"react/dist/react.min.js",
            // "react-dom$":"react-dom/dist/react-dom.min.js",
        }
    },
    module: {
        loaders: [{
                test: /\.js(x?|on)$/,
                loader: 'babel-loader',
                include: [
                    path.join(__dirname, "../static/src/jsx"), //important for performance!
                    path.join(__dirname, "../static/src/js"), //important for performance!
                    path.join(__dirname, "../static/src/Util") //important for performance!
                    // path.join(__dirname, "../static/dest/js"), //important for performance!
                ],
                query: {
                    cacheDirectory: false,
                    presets: ['latest', 'react']
                }
                // loader: 'jsx-loader?insertPragma=React.DOM'
            }, {
                test: /\.less$/,
                exclude: /node_modules|bower_components/,
                loader: ExtractTextPlugin.extract("style-loader", "css-loader!less-loader")
            }, {
                test: /\.git$/,
                loader: "url-loader?mimetype=image/png",
            }, {
                test: /\.woff(2)?(\?v=[0-9].[0-9].[0-9])?$/,
                loader: "url-loader?mimetype=application/font-woff"
            }, {
                test: /\.(ttf|eot|svg)(\?v=[0-9].[0-9].[0-9])?$/,
                loader: "file-loader?name=[name].[ext]"
            }, {
              test: /\.(png|jpg)$/,
              loader: 'url?limit=25000'
            }

        ]
    },
    plugins: [
        // new webpack.optimize.OccurenceOrderPlugin(),
        new webpack.optimize.CommonsChunkPlugin({
            names: [
                "components-bundle",
                "bundle",
            ],
            filename: 'js/[name].js',
            minChunks: Infinity
        }),
        new CopysWebpackPlugin([{
            from: './static/src/css',
            to: './css'
        },
        // {
        //     from: './static/src/fonts',
        //     to: './fonts'
        // },{
        //     from: './static/src/img',
        //     to: './img'
        // },{
        //     from: './static/src/js',
        //     to: './js'
        // }
        ]
        ),
        new webpack.DefinePlugin({
            'process.env.NODE_ENV': '"development"'
        }),
        new ExtractTextPlugin("./css/[name].css")
    ]
}
