var React = require('react');
var ReactDom = require('react-dom');
import Dataset from './dataset'
import {MethodList,MethodKwargs} from './methods'
var _ = require("underscore")
import {Grid,Tab,Row,Nav,NavItem,Navbar,Panel,
ButtonToolbar,Button} from "react-bootstrap"
import {EventStore,newfetch,GetParams} from './components'
import InputGroup from './input'
function paramsReducer(state,action){
    switch(action.type){
        case "method":{
            return _.extend(state,{method:action.data})
        } 
        case "kwargs":{
            return _.extend(state,{kwargs:action.data})

        }
        default:
            return state
    }
}

const PredictProgress = React.createClass({
    childContextTypes:{
        store:React.PropTypes.any
    },
    getInitialState: function() {
        this.store = new EventStore(paramsReducer,{})
        return {
            activeTab:1,
            method:null,
        };
    },
    
    getChildContext() {
        return {store: this.store};
    },
    onMethodChange(data){
        if(data!=this.state.method)
            this.setState({
                method:data
            })
    },
    componentDidMount: function() {
        this.store.addListener("method",this.onMethodChange)
    },
    componentWillUnmount: function() {
        this.store.removeListener("method",this.onMethodChange)
        
    },
    onNextStep(){
        if(this.state.activeTab<2){
            this.setState({activeTab:this.state.activeTab+1})
        }
        else{
            var state = this.store.getState()
            var form = new FormData()
            form.set("action","predict")
            _.forEach(state.kwargs,(value,key)=>{
                form.set(key,value)
            })
            newfetch(`/task/method/${state.method}/`,"POST",
                {"body":form}
            ).then((response)=>{
                return response.json()
            }).then((response_json)=>{
                console.log("onStart response",response_json)
            })

        }
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
                nextBtnDisable=!this.state.method
                break
            }
            case 2:{
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
          <NavItem eventKey={1} disabled={!this.state.dataset}>选择模型</NavItem>
          <NavItem eventKey={2} disabled={!this.state.method}>开始</NavItem>
        </Nav> 
        <ButtonToolbar >
        <Button className="pull-right" 
            bsStyle="primary"
            onClick={this.onNextStep}
            disabled={nextBtnDisable}>{
                this.state.activeTab<2?"下一步":"开始"
            }</Button>
        
        {this.state.activeTab>1?
            <Button className="pull-right" 
            bsStyle="primary" onClick={this.onPrevStep}>上一步</Button>
        :null}
            
        </ButtonToolbar>
        {this.state.activeTab==1?<MethodList public={true} trained={true} />:null}
        {this.state.activeTab==2?<MethodKwargs />:null}
        </div> 

    }
})

export {PredictProgress}