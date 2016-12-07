import { createStore ,applyMiddleware} from 'redux'
var EventEmitter = require('events');
var assign = require('object-assign');
class EventBus extends EventEmitter{
    addListener(event_name,callback) {
        this.on(event_name, callback);
    }
    dispatch(event_name,payload){
        this.emit(event_name,payload)
    }
}
class eventMiddleware{
    constructor(next){
        this.bus = new EventBus()
        return this.middle(next)
    }
    
}
class EventStore {
    constructor(reducer,init_state){
        this.bus = new EventBus()
        var self=this;
        //= =三层匿名函数
        var middle = ({getState})=>{
            return (next)=>(action)=>{
                let returnValue = next(action)
                self.bus.dispatch(action.type,action.data)
                return returnValue
            }
        }
        this.store = createStore(reducer,
                        init_state,
            applyMiddleware(middle))
    }
    getState(){
        return this.store.getState()
    }
    dispatch(action){
        return this.store.dispatch(action)
    }
    addListener(type,callback){
        return this.bus.addListener(type,callback)
    }
    removeListener(type,callback){
        return this.bus.removeListener(type,callback)
    }

}
export default EventStore