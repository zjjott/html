webpackJsonp([2],{

/***/ 0:
/***/ function(module, exports, __webpack_require__) {

	eval("'use strict';\n\nvar _history = __webpack_require__(504);\n\nvar _reactRouter = __webpack_require__(473);\n\nvar _reactBootstrap = __webpack_require__(187);\n\nvar React = __webpack_require__(1);\nvar ReactDom = __webpack_require__(20);\nvar ReactRouter = __webpack_require__(473);\n\nvar history = (0, _reactRouter.useRouterHistory)(_history.createHashHistory)({\n    basename: '/'\n});\nvar Index = React.createClass({\n    displayName: 'Index',\n    render: function render() {\n        return React.createElement(\n            'span',\n            null,\n            '\\u9996\\u9875'\n        );\n    }\n});\nvar Home = React.createClass({\n    displayName: 'Home',\n    render: function render() {\n        return React.createElement(\n            'span',\n            null,\n            '\\u554A'\n        );\n    }\n});\nvar App = React.createClass({\n    displayName: 'App',\n\n    getInitialState: function getInitialState() {\n        return {\n            activeKey: window.location.hash\n        };\n    },\n    handleSelect: function handleSelect(selectedKey) {\n        this.setState({ activeKey: selectedKey }, function () {\n            window.location.hash = selectedKey;\n        });\n    },\n    render: function render() {\n        return React.createElement(\n            _reactBootstrap.Grid,\n            null,\n            React.createElement(\n                _reactBootstrap.Row,\n                { className: 'show-grid' },\n                React.createElement(\n                    _reactBootstrap.Navbar,\n                    null,\n                    React.createElement(\n                        _reactBootstrap.Nav,\n                        { activeKey: this.state.activeKey, onSelect: this.handleSelect },\n                        React.createElement(\n                            _reactBootstrap.NavItem,\n                            { eventKey: \"#/\", href: '#/' },\n                            '\\u9996\\u9875'\n                        ),\n                        React.createElement(\n                            _reactBootstrap.NavItem,\n                            { eventKey: \"#/home\", href: '#/home' },\n                            '\\u7B2C\\u4E8C\\u9875'\n                        )\n                    )\n                )\n            ),\n            React.createElement(\n                _reactBootstrap.Row,\n                { className: 'show-grid' },\n                React.createElement(\n                    _reactBootstrap.Panel,\n                    null,\n                    this.props.children ? this.props.children : React.createElement(Index, null)\n                )\n            )\n        );\n    }\n});\n\nReactDom.render(React.createElement(\n    _reactRouter.Router,\n    { history: history },\n    React.createElement(\n        _reactRouter.Route,\n        { path: '/', component: App },\n        React.createElement(_reactRouter.Route, { path: 'home', component: Home })\n    )\n), document.getElementById(\"container\"));\n\n//////////////////\n// WEBPACK FOOTER\n// ./static/src/jsx/index.jsx\n// module id = 0\n// module chunks = 2\n//# sourceURL=webpack:///./static/src/jsx/index.jsx?");

/***/ },

/***/ 504:
/***/ function(module, exports, __webpack_require__) {

	eval("'use strict';\n\nexports.__esModule = true;\nexports.locationsAreEqual = exports.Actions = exports.useQueries = exports.useBeforeUnload = exports.useBasename = exports.createMemoryHistory = exports.createHashHistory = exports.createHistory = undefined;\n\nvar _LocationUtils = __webpack_require__(51);\n\nObject.defineProperty(exports, 'locationsAreEqual', {\n  enumerable: true,\n  get: function get() {\n    return _LocationUtils.locationsAreEqual;\n  }\n});\n\nvar _createBrowserHistory = __webpack_require__(311);\n\nvar _createBrowserHistory2 = _interopRequireDefault(_createBrowserHistory);\n\nvar _createHashHistory2 = __webpack_require__(312);\n\nvar _createHashHistory3 = _interopRequireDefault(_createHashHistory2);\n\nvar _createMemoryHistory2 = __webpack_require__(313);\n\nvar _createMemoryHistory3 = _interopRequireDefault(_createMemoryHistory2);\n\nvar _useBasename2 = __webpack_require__(168);\n\nvar _useBasename3 = _interopRequireDefault(_useBasename2);\n\nvar _useBeforeUnload2 = __webpack_require__(505);\n\nvar _useBeforeUnload3 = _interopRequireDefault(_useBeforeUnload2);\n\nvar _useQueries2 = __webpack_require__(169);\n\nvar _useQueries3 = _interopRequireDefault(_useQueries2);\n\nvar _Actions2 = __webpack_require__(74);\n\nvar _Actions = _interopRequireWildcard(_Actions2);\n\nfunction _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } else { var newObj = {}; if (obj != null) { for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) newObj[key] = obj[key]; } } newObj.default = obj; return newObj; } }\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }\n\nexports.createHistory = _createBrowserHistory2.default;\nexports.createHashHistory = _createHashHistory3.default;\nexports.createMemoryHistory = _createMemoryHistory3.default;\nexports.useBasename = _useBasename3.default;\nexports.useBeforeUnload = _useBeforeUnload3.default;\nexports.useQueries = _useQueries3.default;\nexports.Actions = _Actions;\n\n//////////////////\n// WEBPACK FOOTER\n// ./~/history/lib/index.js\n// module id = 504\n// module chunks = 2\n//# sourceURL=webpack:///./~/history/lib/index.js?");

/***/ },

/***/ 505:
/***/ function(module, exports, __webpack_require__) {

	eval("'use strict';\n\nexports.__esModule = true;\n\nvar _extends = Object.assign || function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; };\n\nvar _invariant = __webpack_require__(17);\n\nvar _invariant2 = _interopRequireDefault(_invariant);\n\nvar _DOMUtils = __webpack_require__(75);\n\nvar _ExecutionEnvironment = __webpack_require__(109);\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }\n\nvar startListener = function startListener(getPromptMessage) {\n  var handleBeforeUnload = function handleBeforeUnload(event) {\n    var message = getPromptMessage();\n\n    if (typeof message === 'string') {\n      (event || window.event).returnValue = message;\n      return message;\n    }\n\n    return undefined;\n  };\n\n  (0, _DOMUtils.addEventListener)(window, 'beforeunload', handleBeforeUnload);\n\n  return function () {\n    return (0, _DOMUtils.removeEventListener)(window, 'beforeunload', handleBeforeUnload);\n  };\n};\n\n/**\n * Returns a new createHistory function that can be used to create\n * history objects that know how to use the beforeunload event in web\n * browsers to cancel navigation.\n */\nvar useBeforeUnload = function useBeforeUnload(createHistory) {\n  !_ExecutionEnvironment.canUseDOM ?  true ? (0, _invariant2.default)(false, 'useBeforeUnload only works in DOM environments') : (0, _invariant2.default)(false) : void 0;\n\n  return function (options) {\n    var history = createHistory(options);\n\n    var listeners = [];\n    var stopListener = void 0;\n\n    var getPromptMessage = function getPromptMessage() {\n      var message = void 0;\n      for (var i = 0, len = listeners.length; message == null && i < len; ++i) {\n        message = listeners[i].call();\n      }return message;\n    };\n\n    var listenBeforeUnload = function listenBeforeUnload(listener) {\n      if (listeners.push(listener) === 1) stopListener = startListener(getPromptMessage);\n\n      return function () {\n        listeners = listeners.filter(function (item) {\n          return item !== listener;\n        });\n\n        if (listeners.length === 0 && stopListener) {\n          stopListener();\n          stopListener = null;\n        }\n      };\n    };\n\n    return _extends({}, history, {\n      listenBeforeUnload: listenBeforeUnload\n    });\n  };\n};\n\nexports.default = useBeforeUnload;\n\n//////////////////\n// WEBPACK FOOTER\n// ./~/history/lib/useBeforeUnload.js\n// module id = 505\n// module chunks = 2\n//# sourceURL=webpack:///./~/history/lib/useBeforeUnload.js?");

/***/ }

});