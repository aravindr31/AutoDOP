const MongoClient=require('mongodb').MongoClient;
const state={
    db:null
}

module.exports.connect=function(done){

    // const url = 'mongodb://localhost:27017'
    const url = `mongodb+srv://user:microsoft123@cluster0.bibqe.mongodb.net/accounts?retryWrites=true&w=majority`
    const dbname='accounts'


    MongoClient.connect(url, {useUnifiedTopology: true},(err,data)=>{
        if(err) return done(err)
        state.db=data.db(dbname)
        done()
    })
    
}
module.exports.get=function(){
    return state.db
}
