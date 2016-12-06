var React = require('react');
var ReactDom = require('react-dom');
const ReactRouter = require("react-router")
import { createHashHistory} from 'history'
import 'whatwg-fetch'
import { useRouterHistory,Router, Route, Link, IndexLink, browserHistory } from 'react-router'
import {Grid,Tab,Row,Nav,NavItem,Navbar,Panel} from "react-bootstrap"
const history = useRouterHistory(createHashHistory)({
  basename: '/'
})
const Index = React.createClass({
    render(){
        return <span>首页</span>
    }
})
const Home = React.createClass({
    render(){
        return <span>啊</span>
    }
})
const App = React.createClass({
    getInitialState: function() {
        return {
            activeKey:window.location.hash,
            user_id:null
        };
    },
    componentDidMount() {
        fetch("/user/",{credentials:"include"}).then((response)=>{
            return response.json()
        }).then((response_json)=>{
            this.setState(response_json.data)
        })
    },
    handleSelect(selectedKey){
        this.setState({activeKey:selectedKey},()=>{
            window.location.hash = selectedKey
        })
    },
    render(){
        return <Grid>
            <Row className="show-grid">
                <Navbar>
                    <Nav activeKey={this.state.activeKey} onSelect={this.handleSelect}>
                        <NavItem eventKey={"#/"} href="#/">首页</NavItem>
                        <NavItem eventKey={"#/home"} href="#/home">第二页</NavItem>
                    </Nav>
                    <Nav pullRight>
                    {this.state.user_id?
                        <NavItem  href="/user/logout/">{this.state.user_id},Logout</NavItem>:
                        <NavItem  href="/user/login/">Login</NavItem>
                    }
                    </Nav>
                </Navbar>
            </Row>
            <Row className="show-grid">
                <Panel>
                    {this.props.children?this.props.children:<Index />}
                </Panel>
            </Row>
        </Grid>
    }
})

ReactDom.render(<Router history={history}>
    <Route  path="/" component={App}>
      <Route  path="home" component={Home}></Route>
      <Route  path="status" component={Home}></Route>
    </Route>
  </Router>
,document.getElementById("container"))