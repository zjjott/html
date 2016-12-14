var React = require('react');
var ReactDom = require('react-dom');
import Dataset from './dataset'
import {MethodList,MethodKwargs} from './methods'
var _ = require("underscore")
import {Grid,Tab,Row,Nav,NavItem,Navbar,Panel,
ButtonToolbar,Button} from "react-bootstrap"
import {EventStore} from './components'
function paramsReducer(state,action){
    switch(action.type){
        case "dataset":{
            return _.extend(state,{dataset:action.data})
        }
        case "method":{
            return _.extend(state,{method:action.data})
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
            method:null,
        };
    },
    onDatasetChange(data){
        if(data!=this.state.dataset)
            this.setState({
                dataset:data
            })
    },
    onMethodChange(data){
        console.log("method",data)
        if(data!=this.state.method)
            this.setState({
                method:data
            })
    },
    getChildContext() {
        return {store: this.store};
    },
    componentDidMount: function() {
        this.store.addListener("dataset",this.onDatasetChange)
        this.store.addListener("method",this.onMethodChange)
    },
    componentWillUnmount: function() {
        this.store.removeListener("dataset",this.onDatasetChange)
        this.store.removeListener("method",this.onMethodChange)
        
    },
    onNextStep(){
        this.setState({activeTab:this.state.activeTab+1})
    },
    onPrevStep(){
        this.setState({activeTab:this.state.activeTab-1})
    },
    handleSelect(selectedKey) {
        this.setState({activeTab:selectedKey})
    },
    render(){
        var nextBtnDisable;
        switch(this.state.activeTab)
        {
            case 1:{
                nextBtnDisable=!this.state.dataset
                break
            }
            case 2:{
                nextBtnDisable=!this.state.method
                break
            }
            case 3:{
                nextBtnDisable=false   
                break
            }
            default:
                nextBtnDisable=true
        }
        return <div>
        <Nav bsStyle="tabs" 
        justified 
        activeKey={this.state.activeTab} 
        onSelect={this.handleSelect}>
          <NavItem eventKey={1} >选择数据集
          </NavItem>
          <NavItem eventKey={2} disabled={!this.state.dataset}>选择模型</NavItem>
          <NavItem eventKey={3} disabled={!this.state.method}>开始</NavItem>
        </Nav> 
        <ButtonToolbar >
        <Button className="pull-right" 
            bsStyle="primary"
            onClick={this.onNextStep}
            disabled={nextBtnDisable}>下一步</Button>
        {this.state.activeTab>1?
            <Button className="pull-right" 
            bsStyle="primary" onClick={this.onPrevStep}>上一步</Button>
        :null}
            
        </ButtonToolbar>
        {this.state.activeTab==1?<Dataset />:null}
        {this.state.activeTab==2?<MethodList />:null}
        {this.state.activeTab==3?<MethodKwargs />:null}


        </div> 

    }
})

export {TrainProgress}