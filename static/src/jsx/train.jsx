var React = require('react');
var ReactDom = require('react-dom');
import Dataset from './dataset'
var _ = require("underscore")
import {Grid,Tab,Row,Nav,NavItem,Navbar,Panel} from "react-bootstrap"
import {EventStore} from './components'
function paramsReducer(state,action){
    switch(action.type){
        case "dataset":{
            return _.extend(state,{dataset:action.data})
        }
        default:
            return state
    }
}
const TrainProgress = React.createClass({
    childContextTypes:{
        store:React.PropTypes.any
    },
    getInitialState: function() {
        this.store = new EventStore(paramsReducer,{})
        return {
            activeTab:1,
            dataset:null,
            model:null,
        };
    },
    onDatasetChange(data){
        if(data!=this.state.dataset)
            this.setState({
                dataset:data
            })
    },
    getChildContext() {
        return {store: this.store};
    },
    componentDidMount: function() {
        this.store.addListener("dataset",this.onDatasetChange)
    },
    componentWillUnmount: function() {
        this.store.removeListener("dataset",this.onDatasetChange)
        
    },
    handleSelect(selectedKey) {
        this.setState({activeTab:selectedKey})
    },
    render(){

        return <div>
        <Nav bsStyle="tabs" 
        justified 
        activeKey={this.state.activeTab} 
        onSelect={this.handleSelect}>
          <NavItem eventKey={1} >选择数据集
          </NavItem>
          <NavItem eventKey={2} disabled={!this.state.dataset}>选择模型</NavItem>
          <NavItem eventKey={3} disabled={!this.state.model}>开始</NavItem>
        </Nav>
        {this.state.activeTab==1?<Dataset />:null}
        </div> 

    }
})

export {TrainProgress}