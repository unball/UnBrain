#ifndef SERVERIGGLU_H
#define SERVERIGGLU_H

#include <QObject>
#include <QtCore/QList>
#include <QtWebSockets/QWebSocket>

class ServerIgglu : public QObject
{
    Q_OBJECT
public:
    explicit ServerIgglu(QObject *parent = nullptr);
    void connectWebSocket(quint16 port);
    void closeWebSocket();
    void disconnectWebSocket();
    void sendMessage();
    ~ServerIgglu() override;

private slots:
    void onConnected();
    void closed();
    void processMessage(const QString &message);
    void onDisconnected(){
        qDebug() << "Disconnected";
    }

private:
    QWebSocket m_webSocket;
    QList<QWebSocket *> m_clients;
};

#endif // SERVERIGGLU_H
