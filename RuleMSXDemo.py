# RuleMSXDemo.py

from EasyMSX import EasyMSX
from rulemsx import RuleMSX
from rulecondition import RuleCondition
from ruleevaluator import RuleEvaluator
from action import Action
from datapointsource import DataPointSource

class RuleMSXDemo:
    
    def __init__(self):

        print("Initialising RuleMSX...")
        self.ruleMSX = RuleMSX()
        print("RuleMSX initialised...")
        
        
        print("Initialising EasyMSX...")
        self.easyMSX = EasyMSX()
        print("EasyMSX initialised...")
        
        self.easyMSX.orders.addNotificationHandler(self.processNotification)
        self.easyMSX.routes.addNotificationHandler(self.processNotification)

        print("Create RuleSet...")
        self.buildRules()
        print("RuleSet ready...")

        self.easyMSX.start()
             
    class StringEqualityEvaluator(RuleEvaluator):
        
        def __init__(self, dataPointName, targetValue):
            self.dataPointName = dataPointName
            self.targetValue = targetValue
            super().addDependentDataPointName(dataPointName)
        
        def evaluate(self,dataSet):
            dpValue = dataSet.dataPoints[self.dataPointName].getValue()
            return dpValue==self.targetValue
        
    class SendMessageWithDataPointValue(Action):
        
        def __init__(self,msgStr, dataPointName):
            self.msgStr = msgStr
            self.dataPointName = dataPointName
            
        def execute(self,dataSet):
            dpValue = dataSet.dataPoints[self.dataPointName].getValue()
            print (self.msgStr + dpValue)
            
        
    class ShowFillEvent(Action):
        
        def __init__(self, easyMSX):
            self.easyMSX = easyMSX
        
        def execute(self,dataSet):
            dpOrderNo = dataSet.dataPoints["OrderNumber"].getValue()
            o = self.easyMSX.orders.getBySequenceNo(int(dpOrderNo))
            if int(o.field("EMSX_WORKING").value()) == 0:
                print("Completed: " + dpOrderNo)
            else:
                print("PartFilled: " + dpOrderNo)
            
    class EMSXFieldDataPointSource(DataPointSource):

        def __init__(self, field):
            self.source = field
            field.addNotificationHandler(self.processNotification)
            
        def getValue(self):
            return self.source.value()
        
        def processNotification(self, notification):
            super().setStale()
            
            
    def buildRules(self):
        
        condStatusNew = RuleCondition("OrderStatusIsNew", self.StringEqualityEvaluator("OrderStatus","NEW"))
        condStatusWorking = RuleCondition("OrderStatusIsWorking", self.StringEqualityEvaluator("OrderStatus","WORKING"))
        condStatusPartFilled = RuleCondition("OrderStatusIsPartFilled", self.StringEqualityEvaluator("OrderStatus","PARTFILL"))
        condStatusFilled = RuleCondition("OrderStatusIsFilled", self.StringEqualityEvaluator("OrderStatus","FILLED"))

        #condUSExchange = RuleCondition("IsUSExchange", self.StringEqualityEvaluator("Exchange","US"))
        #condLNExchange = RuleCondition("IsLNExchange", self.StringEqualityEvaluator("Exchange","LN"))

        #condPercentFilled = RuleCondition("Route50%Filled", self.PercentageFilledEvaluator(50))
        
        #actionSetDestBrokerBB = self.ruleMSX.createAction("SetDestBroker", self.SetDestinationBroker("BB"))
        #actionSetDestBrokerBMTB = self.ruleMSX.createAction("SetDestBroker", self.SetDestinationBroker("BMTB"))
        #actionRouteOrder = self.ruleMSX.createAction("RouteOrder", self.RouteOrder())
        
        actionSendNewMessage = self.ruleMSX.createAction("SendNewMessage", self.SendMessageWithDataPointValue("New Order Created: ", "OrderNumber"))
        actionSendAckMessage = self.ruleMSX.createAction("SendAckMessage", self.SendMessageWithDataPointValue("Broker Acknowledged Route: ", "OrderNumber"))
        actionSendFillMessage = self.ruleMSX.createAction("SendFillMessage", self.ShowFillEvent(self.easyMSX))
        
        #actionShowOrderDetails = self.ruleMSX.createAction("ShowOrderDetails", self.ShowOrderDetails())
        #actionShowRouteDetails = self.ruleMSX.createAction("ShowRouteDetails", self.ShowRouteDetails())
        #actionCancelRoute = self.ruleMSX.createAction("CancelRoute", self.CancelRoute())
        
        demoRuleSet = self.ruleMSX.createRuleSet("demoRuleSet")

        ruleNewOrder = demoRuleSet.addRule("NewOrder")
        ruleNewOrder.addRuleCondition(condStatusNew)
        ruleNewOrder.addAction(actionSendNewMessage)
        
        ruleWorkingOrder = demoRuleSet.addRule("WorkingOrder")
        ruleWorkingOrder.addRuleCondition(condStatusWorking)
        ruleWorkingOrder.addAction(actionSendAckMessage)
        
        rulePartFilledOrder = demoRuleSet.addRule("PartFilledOrder")
        rulePartFilledOrder.addRuleCondition(condStatusPartFilled)
        rulePartFilledOrder.addAction(actionSendFillMessage)
        
        ruleFilledOrder = demoRuleSet.addRule("FilledOrder")
        ruleFilledOrder.addRuleCondition(condStatusFilled)
        ruleFilledOrder.addAction(actionSendFillMessage)

        #ruleSetUSDestBroker = demoRuleSet.addRule("SetUSDestBroker")
        #ruleSetUSDestBroker.addRuleCondition(condUSExchange)
        #ruleSetUSDestBroker.addRuleCondition(condStatusNew)
        
        #ruleRouteOrder = demoRuleSet.addRule("RouteOrder")
        

    def processNotification(self,notification):

        if notification.category == EasyMSX.NotificationCategory.ORDER:
            if notification.type == EasyMSX.NotificationType.NEW or notification.type == EasyMSX.NotificationType.INITIALPAINT: 
            #    print("EasyMSX Event (NEW/INITALPAINT): " + notification.source.field("EMSX_SEQUENCE").value())
            #if notification.type == EasyMSX.NotificationType.UPDATE or notification.type == EasyMSX.NotificationType.CANCEL or notification.type == EasyMSX.NotificationType.DELETE: 
            #    print("EasyMSX Event (UPD/CANCEL/DELETE): " + notification.source.field("EMSX_SEQUENCE").value())
                self.parseOrder(notification.source)
        
        if notification.category == EasyMSX.NotificationCategory.ROUTE:
            if notification.type == EasyMSX.NotificationType.NEW or notification.type == EasyMSX.NotificationType.INITIALPAINT: 
            #    print("EasyMSX Event (NEW/INITALPAINT): " + notification.source.field("EMSX_SEQUENCE").value())
            #if notification.type == EasyMSX.NotificationType.UPDATE or notification.type == EasyMSX.NotificationType.CANCEL or notification.type == EasyMSX.NotificationType.DELETE: 
            #    print("EasyMSX Event (UPD/CANCEL/DELETE): " + notification.source.field("EMSX_SEQUENCE").value())
                self.parseOrder(notification.source)
            


        
    def parseOrder(self,o):
        
        newDataSet = self.ruleMSX.createDataSet("DS" + o.field("EMSX_SEQUENCE").value())

        newDataSet.addDataPoint("OrderStatus", self.EMSXFieldDataPointSource(o.field("EMSX_STATUS")))
        newDataSet.addDataPoint("OrderNumber", self.EMSXFieldDataPointSource(o.field("EMSX_SEQUENCE")))

        self.ruleMSX.ruleSets["demoRuleSet"].execute(newDataSet)


if __name__ == '__main__':
    
    ruleMSXDemo = RuleMSXDemo();
    
    input("Press any to terminate")

    print("Terminating...\n")

    quit()
    