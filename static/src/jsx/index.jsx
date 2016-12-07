var React = require('react');
var ReactDom = require('react-dom');
const ReactRouter = require("react-router")
import { createHashHistory} from 'history'
import {newfetch,} from "./components"
import { useRouterHistory,Router, Route, Link, IndexLink, browserHistory } from 'react-router'
import {Grid,Tab,Row,Nav,NavItem,Navbar,Panel} from "react-bootstrap"
import {ProgressBar,Table,Well} from "react-bootstrap"
const _ = require("underscore")

import {TrainProgress} from './train'
import {PredictProgress} from './predict'
const history = useRouterHistory(createHashHistory)({
  basename: '/'
})


const AppStatus = React.createClass({
    getInitialState: function() {
        return {
            queue:{} 
        };
    },
    componentDidMount() {
        newfetch("/task/queue/").then((response)=>{
            return response.json()
        }).then((response_json)=>{
            this.setState({"queue":response_json.data})
        })
    },
    render(){
        return <div>
        <Well >任务队列状态</Well>
        <Table  condensed responsive striped>
        <tbody>
            {_.map(this.state.queue,(value,key)=>{
                return <tr key={key}>
                    <td className="col-lg-2">{key}总量:{value.total}</td>
                    <td className="col-lg-10">
                    <ProgressBar 
                    max={value.total} 
                    now={value.active}
                    label={`工作中:${value.active}`}
                    />  </td>
                </tr>
            })}
            </tbody>
        </Table>
        </div>
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
                        <NavItem eventKey={"#/"} href="#/">训练</NavItem>
                        <NavItem eventKey={"#/predict"} href="#/predict">预测</NavItem>
                        <NavItem eventKey={"#/status"} href="#/status">系统状态</NavItem>
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
                    {this.props.children?this.props.children:<TrainProgress />}
                </Panel>
            </Row>
        </Grid>
    }
})

ReactDom.render(<Router history={history}>
    <Route  path="/" component={App}>
      <Route  path="status" component={AppStatus}></Route>
      <Route  path="predict" component={PredictProgress}></Route>
    </Route>
  </Router>
,document.getElementById("container"))